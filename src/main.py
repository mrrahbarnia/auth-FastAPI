import logging
from logging.config import dictConfig

from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from richapi import enrich_openapi # type: ignore

from src.config import LogConfig
from src.config import app_configs
from src.auth import router as auth_router

logger = logging.getLogger("root")


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    dictConfig(LogConfig().model_dump())
    logger.info("App is running...")
    yield

app = FastAPI(**app_configs, lifespan=lifespan)

app.openapi = enrich_openapi(app) # type: ignore


app.include_router(router=auth_router.router, prefix="/auth", tags=["auth"])