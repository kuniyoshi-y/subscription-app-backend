from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:3000"

    COGNITO_REGION: str = "ap-northeast-1"
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""

    # ローカル開発用（本番は必ずfalseにする）
    DEV_MODE: bool = False
    DEV_USER_ID: str = "00000000-0000-0000-0000-000000000001"

settings = Settings()
