# pydantic v2: BaseSettings вынесен в пакет pydantic_settings
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = Field(..., env='DATABASE_URL')

    # Redis settings
    REDIS_URL: str = Field(..., env='REDIS_URL')

    # Celery settings
    CELERY_BROKER_URL: Optional[str] = Field(None, env='CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND: Optional[str] = Field(None, env='CELERY_RESULT_BACKEND')

    # Sentry
    SENTRY_DSN: str = Field(None, env='SENTRY_DSN')

    # JWT settings
    SECRET_KEY: str = Field(..., env='SECRET_KEY')
    ALGORITHM: str = Field('HS256', env='ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env='ACCESS_TOKEN_EXPIRE_MINUTES')

    # AWS S3 / Object storage
    S3_ACCESS_KEY: str = Field(None, env='S3_ACCESS_KEY')
    S3_SECRET_KEY: str = Field(None, env='S3_SECRET_KEY')
    S3_BUCKET_NAME: str = Field(None, env='S3_BUCKET_NAME')
    S3_ENDPOINT_URL: str = Field(None, env='S3_ENDPOINT_URL')

    # pydantic v2 -> model_config вместо класса Config
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

# Singleton for app
settings = Settings() 