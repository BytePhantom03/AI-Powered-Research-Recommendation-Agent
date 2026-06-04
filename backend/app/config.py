from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./research_agent.db"
    REDIS_URL: str = "" # Not used in local fallback
    CELERY_BROKER_URL: str = "" # Not used in local fallback
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    SECRET_KEY: str = "supersecretkey"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
