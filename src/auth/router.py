from typing import Annotated
from redis.asyncio import Redis
from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth.service import UserService
from src.auth.models import User
from src.auth.type import TokensDict
from src.auth.schemas import RegisterIn, RegisterOut, VerifyIn, RefreshTokenIn
from src.database import session_maker, redis_conn
from src.auth.dependencies import current_user

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterOut
)
async def register(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(session_maker)
    ],
    redis: Annotated[Redis, Depends(redis_conn)],
    payload: RegisterIn
) -> dict:
    """
    **Passwords** must be:
    - At least 8 chars
    """
    await UserService(session_maker).register(redis, payload)
    return {"email": payload.email}


@router.post(
    "/verification",
    status_code=status.HTTP_200_OK
)
async def verification(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(session_maker)
    ],
    redis: Annotated[Redis, Depends(redis_conn)],
    payload: VerifyIn
) -> dict:
    await UserService(session_maker).verification(redis, payload)
    return {"detail": "Verified successfully."}


@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
async def login(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(session_maker)
    ],
    redis: Annotated[Redis, Depends(redis_conn)],
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    tokens = await UserService(session_maker).login(
        redis, email=payload.username, password=payload.password
    )
    return {
        "email": payload.username,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }


@router.get(
    "/me",
    status_code=status.HTTP_200_OK
)
async def me(
    user: Annotated[User, Depends(current_user)]
) -> dict:
    return {"email": user.email}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK
)
async def refresh_token(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(session_maker)
    ],
    redis: Annotated[Redis, Depends(redis_conn)],
    payload: RefreshTokenIn
) -> TokensDict:
    tokens = await UserService(session_maker).refresh(redis, payload.refresh_token)
    return tokens
