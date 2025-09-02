import os
import sys
from sqlalchemy import create_engine
from app.db.base import Base
from app.models import *  # Import all models to register them with SQLAlchemy

def init_db():
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/resume_db")
    
    # Create engine and connect to database
    engine = create_engine(database_url)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    # Add the project root to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    init_db()
