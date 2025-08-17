from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"
    API_SECRET_KEY: str = "a_very_secret_key_that_should_be_in_env" # Default for local dev

    # S3 settings
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET: str = "ai-pricing-negotiation"

    class Config:
        # The .env file should be in the root of the project, where docker-compose is run
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields from .env

settings = Settings()
