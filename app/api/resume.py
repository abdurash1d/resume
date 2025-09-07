from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import crud, schemas, models
from ..db.base import get_db
from ..core.security import get_current_active_user
from ..crud import resume_history as crud_history
from ..schemas import resume_history as schemas_history

router = APIRouter(prefix="/resumes", tags=["resumes"])

@router.post("/", response_model=schemas.resume.ResumeInDB)
def create_resume(
    resume: schemas.resume.ResumeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new resume for the current user.
    """
    return crud.resume.create_resume(db=db, resume=resume, user_id=current_user.id)

@router.get("/", response_model=List[schemas.resume.ResumeInDB])
def read_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve all resumes for the current user.
    """
    return crud.resume.get_resumes(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{resume_id}", response_model=schemas.resume.ResumeWithHistory)
def read_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a specific resume by ID with its history.
    """
    resume = crud.resume.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    history = crud.resume.get_resume_history(db, resume_id=resume_id, user_id=current_user.id)
    
    return {
        **resume.__dict__,
        "history": history
    }

@router.put("/{resume_id}", response_model=schemas.resume.ResumeInDB)
def update_resume(
    resume_id: int,
    resume_update: schemas.resume.ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a resume.
    """
    return crud.resume.update_resume(
        db=db, 
        resume_id=resume_id, 
        resume_update=resume_update, 
        user_id=current_user.id
    )


@router.get("/{resume_id}/history", response_model=List[schemas_history.ResumeHistory])
async def get_resume_history(
    resume_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get improvement history for a resume.
    """
    # Verify the resume belongs to the user
    resume = crud.resume.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return crud_history.get_resume_history(db, resume_id=resume_id, skip=skip, limit=limit)

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a resume.
    """
    crud.resume.delete_resume(db=db, resume_id=resume_id, user_id=current_user.id)
    return {"ok": True}

@router.post("/{resume_id}/improve", response_model=schemas.resume.ResumeInDB)
def improve_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Improve a resume using AI.
    """
    return crud.resume.improve_resume(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id
    )
