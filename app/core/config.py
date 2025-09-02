from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    DEBUG: bool = False
    PROJECT_NAME: str = "Resume Manager"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database settings
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/resume_db"
    TEST_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/test_resume_db"
    
    # Security
    ALGORITHM: str = "HS256"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create an instance of settings
settings = Settings()
