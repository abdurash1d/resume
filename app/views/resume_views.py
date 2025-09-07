from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.base import get_db
from ..models.user import User
from ..models.resume import Resume, ResumeHistory
from ..schemas.resume import ResumeCreate, ResumeUpdate, ResumeImprove
from ..crud import resume as crud_resume
from ..core.security import get_current_active_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/resumes", response_class=HTMLResponse)
async def list_resumes(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all resumes for the current user"""
    resumes = crud_resume.get_resumes(db, user_id=current_user.id, skip=skip, limit=limit)
    return templates.TemplateResponse(
        "resumes/list.html",
        {"request": request, "resumes": resumes, "user": current_user}
    )

@router.get("/resumes/new", response_class=HTMLResponse)
async def new_resume_form(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Show form to create a new resume"""
    return templates.TemplateResponse(
        "resumes/form.html",
        {"request": request, "resume": None, "user": current_user}
    )

@router.get("/resumes/{resume_id}", response_class=HTMLResponse)
async def view_resume(
    request: Request,
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """View a specific resume"""
    resume = crud_resume.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Get resume history
    history = crud_resume.get_resume_history(
        db, resume_id=resume_id, user_id=current_user.id
    )
    
    return templates.TemplateResponse(
        "resumes/detail.html",
        {
            "request": request, 
            "resume": resume,
            "history": history,
            "user": current_user
        }
    )

@router.get("/resumes/{resume_id}/edit", response_class=HTMLResponse)
async def edit_resume_form(
    request: Request,
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Show form to edit a resume"""
    resume = crud_resume.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    return templates.TemplateResponse(
        "resumes/form.html",
        {"request": request, "resume": resume, "user": current_user}
    )

# Add these routes to your FastAPI app in main.py
# from app.views import resume_views
# app.include_router(resume_views.router, tags=["resume_views"])
