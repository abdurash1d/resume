from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    DEBUG: bool = False
    PROJECT_NAME: str = "Resume Manager"
    API_V1_STR: str = "/api"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database settings
    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None

    # Security
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True
        # By not specifying env_file, pydantic-settings will prioritize
        # environment variables, which Docker Compose provides from .env.prod.

# Create an instance of settings
settings = Settings()
