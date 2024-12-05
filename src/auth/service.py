import sqlalchemy as sa

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth import exceptions
from src.auth.config import auth_config
from src.auth.models import User
from src.auth.type import UserId, TokensDict, DecodedRefreshToken
from src.auth.schemas import RegisterIn, VerifyIn
from src.auth.utils import (
    get_password_hash,
    generate_random_code,
    verify_password,
    encode_tokens,
    decode_refresh_token
)


class UserService:
    REFRESH_TOKEN_EXPIRE_SECONDS = auth_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker

    async def get_user_by_id(self, user_id: UserId) -> User | None:
        smtm = sa.select(User).where(User.id==user_id)
        async with self.session_maker.begin() as conn:
            return await conn.scalar(smtm)

    async def register(self, redis_conn: Redis, payload: RegisterIn) -> None:
        select_smtm = sa.select(User).where(User.email==payload.email)
        async with self.session_maker.begin() as conn:
            user: tuple[User] | None = (await conn.execute(select_smtm)).tuples().first()
            if user:
                raise exceptions.DuplicateEmail
            else:
                hashed_password = get_password_hash(payload.password)
                insert_smtm = sa.insert(User).values({
                    User.email: payload.email,
                    User.password: hashed_password
                })
                await conn.execute(insert_smtm)

        try: # Unit of work
            await redis_conn.set(
                name=generate_random_code(),
                value=payload.email,
                ex=auth_config.VALIDATION_MESSAGE_LIFETIME_SEC
            )
            # Send an email for authenticated user
        except Exception as ex:
            print(ex)

    async def verification(self, redis_conn: Redis, payload: VerifyIn) -> None:
        cached_email = await redis_conn.getdel(name=payload.verification_code)
        if not cached_email:
            raise exceptions.ExpiredOrInvalidCode
        else:
            smtm = sa.update(User).values({
                User.is_active: True
            }).where(User.email==cached_email).returning(User.id)
            async with self.session_maker.begin() as conn:
                user_id: UserId | None = await conn.scalar(smtm)
                if not user_id:
                    raise exceptions.SomethingWentWrong

    async def login(self, redis_conn: Redis, email: str, password: str) -> TokensDict:
        stmt = sa.select(User).where(User.email==email)
        async with self.session_maker.begin() as conn:
            user: User | None = await conn.scalar(stmt)
            if (not user) or (not verify_password(password, user.password)):
                raise exceptions.InvalidCredentials
            if not user.is_active:
                raise exceptions.NotActiveAccount
        access_token = encode_tokens("access_token", user.id, user.email, user.role)
        refresh_token = encode_tokens("refresh_token", user.id)

        await redis_conn.set(
            name=f"refresh-token:user-id:{user.id}",
            value=refresh_token,
            ex=UserService.REFRESH_TOKEN_EXPIRE_SECONDS
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    async def refresh(self, redis_conn: Redis, refresh_token: str) -> TokensDict:
        data: DecodedRefreshToken = await decode_refresh_token(refresh_token)
        if cached_token := await redis_conn.getdel(f"refresh-token:user-id:{data['user_id']}"):
            if cached_token != refresh_token:
                raise exceptions.WrongRefreshToken
            user = await self.get_user_by_id(data["user_id"])
            if not user:
                raise exceptions.WrongRefreshToken
            new_access_token = encode_tokens("access_token", user.id, user.email, user.role)
            new_refresh_token = encode_tokens("refresh_token", user.id)
            await redis_conn.set(
                name=refresh_token,
                value=user.id,
                ex=UserService.REFRESH_TOKEN_EXPIRE_SECONDS
            )
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token
            }
        raise exceptions.WrongRefreshToken
