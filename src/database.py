import redis.asyncio as redis

from typing import AsyncGenerator
from sqlalchemy import MetaData, INTEGER, String
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from src.config import settings
from src.auth.type import UserId, UserRole

DB_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase, MappedAsDataclass):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
    type_annotation_map = {
        UserId: INTEGER,
        UserRole: String
    }

async_engine: AsyncEngine = create_async_engine(str(settings.POSTGRES_URL))


async def session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(async_engine, expire_on_commit=False)


async def redis_conn() -> AsyncGenerator[redis.Redis, None]:
    client = redis.Redis.from_url(url=str(settings.REDIS_URL))
    try:
        yield client
    finally:
        await client.aclose()
