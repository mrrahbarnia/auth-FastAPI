import jwt

from typing import Literal, overload
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext # type: ignore

from src.auth.type import DecodedRefreshToken
from src.auth.exceptions import WrongRefreshToken
from src.auth.config import auth_config
from src.auth.type import UserRole, UserId


ACCESS_SECRET_KEY = auth_config.ACCESS_SECRET_KEY
REFRESH_SECRET_KEY = auth_config.REFRESH_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = auth_config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = auth_config.REFRESH_TOKEN_EXPIRE_DAYS
JWT_ALGORITHM = auth_config.JWT_ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_random_code() -> str:
    return uuid4().hex[:6]


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(passoword: str, hashed_password: str) -> bool:
    return pwd_context.verify(passoword, hashed_password)


@overload
def encode_tokens(
    token_type: Literal["access_token"],
    user_id: UserId,
    email: str,
    user_role: UserRole
) -> str:...

@overload
def encode_tokens(
    token_type: Literal["refresh_token"],
    user_id: UserId
) -> str:...


def encode_tokens(
    token_type: Literal["access_token", "refresh_token"],
    user_id: UserId,
    email: str | None = None,
    user_role: UserRole | None = None
) -> str:
    time_delta = (
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) if
        token_type == "access_token" else
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    secret_key = ACCESS_SECRET_KEY if token_type == "access_token" else REFRESH_SECRET_KEY
    payload = {
        "user_id": user_id,
        "exp": datetime.now(tz=timezone.utc) + time_delta
    }
    if token_type == "access_token" and user_role:
        payload.update({
            "user_email": email,
            "user_role": user_role.value,
        })
    token = jwt.encode(payload, secret_key, JWT_ALGORITHM)
    return token


async def decode_refresh_token(token: str) -> DecodedRefreshToken:
    try:
        data = jwt.decode(jwt=token, key=REFRESH_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise WrongRefreshToken
    return data
