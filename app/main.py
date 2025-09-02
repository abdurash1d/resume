from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
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

# Include API routers
from .api import auth, resume
app.include_router(auth.router)
app.include_router(resume.router, prefix="/api")

# Mount static files
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user
    })

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
