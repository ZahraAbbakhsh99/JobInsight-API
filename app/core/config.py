# app/core/config.py
from pydantic import EmailStr, PostgresDsn, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # General
    APP_NAME: str = "JobInsight"
    DEBUG: bool = False

    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: EmailStr
    SMTP_PASS: str
    FROM_EMAIL: EmailStr

    # Auth
    JWT_SECRET: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_HOURS: int = 24
    OTP_EXPIRE_MINUTES: int = 10

    # Database
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str
    POSTGRES_DB : str
    POSTGRES_HOST : str = "localhost"
    POSTGRES_PORT : int =5432

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
