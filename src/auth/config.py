from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_ALGORITHM: str
    VALIDATION_MESSAGE_LIFETIME_SEC: int


auth_config = AuthConfig() # type: ignore