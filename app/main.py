from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from .core.security import JWTAuthBackend
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging
from .core.config import settings
from .core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

from . import crud, models, schemas
from .db.base import Base, engine, get_db
from .core.security import get_current_active_user, get_current_user_from_token

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Manager API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(
    AuthenticationMiddleware,
    backend=JWTAuthBackend()
)

# Include API routers
from .api import auth, resume
app.include_router(auth.router)
app.include_router(resume.router, prefix="/api")

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
import os
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
templates = Jinja2Templates(directory=templates_dir)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = None
    token = request.cookies.get("access_token")
    if token:
        try:
            from .core.security import get_current_user
            from fastapi import Depends
            from fastapi.security import OAuth2PasswordBearer
            from .db.base import get_db
            from jose import JWTError, jwt
            import os
            
            SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
            ALGORITHM = os.getenv("ALGORITHM", "HS256")
            
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    from .models.user import User
                    user = db.query(User).filter(User.email == email).first()
            except JWTError:
                pass
        except Exception as e:
            print(f"Error getting user: {e}")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user)
):
    # If we get here, the user is authenticated
    try:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": current_user
        })
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while loading the dashboard"
        )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/login")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/resumes", response_class=HTMLResponse)
async def resumes_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse("resumes.html", {
        "request": request,
        "user": current_user
    })

@app.get("/resumes/new", response_class=HTMLResponse)
async def new_resume_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse("resume_form.html", {
        "request": request,
        "user": current_user
    })

@app.get("/resumes/{resume_id}", response_class=HTMLResponse)
async def resume_detail_page(
    request: Request,
    resume_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resume = crud.resume.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return templates.TemplateResponse("resume_detail.html", {
        "request": request,
        "user": current_user,
        "resume": resume,
        "resume_id": resume_id
    })

@app.get("/resumes/{resume_id}/edit", response_class=HTMLResponse)
async def edit_resume_page(
    request: Request,
    resume_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resume = crud.resume.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return templates.TemplateResponse("resume_form.html", {
        "request": request,
        "user": current_user,
        "resume": resume
    })

# API endpoints for frontend
@app.get("/api/resumes", response_model=List[schemas.resume.ResumeInDB])
async def get_user_resumes(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for the current user"""
    return crud.resume.get_resumes(db, user_id=current_user.id, skip=skip, limit=limit)

@app.get("/api/resumes/{resume_id}/history")
async def get_resume_history(
    resume_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get improvement history for a resume"""
    # Verify the resume belongs to the user
    resume = crud.resume.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    history = crud.resume.get_resume_history(db, resume_id=resume_id, user_id=current_user.id)
    return jsonable_encoder(history)

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")

# Create static directory if it doesn't exist
os.makedirs("app/static", exist_ok=True)
