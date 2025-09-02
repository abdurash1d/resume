# Import all models here for proper initialization
from app.models.user import User
from app.models.resume import Resume, ResumeHistory

# This makes sure SQLAlchemy discovers all models
__all__ = ['User', 'Resume', 'ResumeHistory']
