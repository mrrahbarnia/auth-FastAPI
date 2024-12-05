from typing import NewType, TypedDict, Literal
from enum import Enum

UserId = NewType('UserId', int)


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class TokensDict(TypedDict):
    access_token: str
    refresh_token: str


class DecodedRefreshToken(TypedDict):
    user_id: UserId
    exp: int


class DecodedAccessToken(DecodedRefreshToken):
    user_email: str
    user_role: Literal['admin', 'user']
