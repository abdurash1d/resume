from .user import get_user_by_email, create_user, authenticate_user
from .resume import (
    get_resume, get_resumes, create_resume, 
    update_resume, delete_resume, improve_resume,
    get_resume_history
)

# This makes the functions available when importing from app.crud
__all__ = [
    'get_user_by_email', 'create_user', 'authenticate_user',
    'get_resume', 'get_resumes', 'create_resume',
    'update_resume', 'delete_resume', 'improve_resume',
    'get_resume_history'
]
