import jwt

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from src.auth.service import UserService
from src.auth.models import User
from src.database import session_maker
from src.auth.type import DecodedAccessToken
from src.auth.config import auth_config
from src.auth.exceptions import ForbiddenException, NotActiveAccount


ACCESS_SECRET_KEY = auth_config.ACCESS_SECRET_KEY
JWT_ALGORITHM = auth_config.JWT_ALGORITHM

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/login")


async def decode_access_token(
        token: Annotated[str, Depends(oauth2_schema)]
) -> DecodedAccessToken:
    try:
        data = jwt.decode(jwt=token, key=ACCESS_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise ForbiddenException
    return data


async def current_user(
    decoded_data: Annotated[DecodedAccessToken, Depends(decode_access_token)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(session_maker)]
) -> User:
    if "user_id" not in decoded_data:
        raise ForbiddenException
    user_id = decoded_data["user_id"]
    user: User | None = await UserService(session).get_user_by_id(user_id)
    if not user:
        raise ForbiddenException
    if not user.is_active:
        raise NotActiveAccount
    return user
