from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.resume import Resume, ResumeHistory
from ..schemas.resume import ResumeCreate, ResumeUpdate, ResumeImprove

def get_resume(db: Session, resume_id: int, user_id: int) -> Optional[Resume]:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume

def get_resumes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Resume]:
    return db.query(Resume).filter(Resume.user_id == user_id).offset(skip).limit(limit).all()

def create_resume(db: Session, resume: ResumeCreate, user_id: int) -> Resume:
    db_resume = Resume(**resume.dict(), user_id=user_id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    # Create history entry
    history_entry = ResumeHistory(
        resume_id=db_resume.id,
        content=resume.content
    )
    db.add(history_entry)
    db.commit()
    
    return db_resume

def update_resume(
    db: Session, 
    resume_id: int, 
    resume_update: ResumeUpdate, 
    user_id: int
) -> Resume:
    db_resume = get_resume(db, resume_id, user_id)
    
    update_data = resume_update.dict(exclude_unset=True)
    
    # Create history entry before updating
    if 'content' in update_data:
        history_entry = ResumeHistory(
            resume_id=resume_id,
            content=db_resume.content,
            improved_content=update_data.get('content'),
            created_at=datetime.utcnow()
        )
        db.add(history_entry)
    
    # Update the resume
    for field, value in update_data.items():
        setattr(db_resume, field, value)
    
    db.commit()
    db.refresh(db_resume)
    return db_resume

def delete_resume(db: Session, resume_id: int, user_id: int) -> None:
    db_resume = get_resume(db, resume_id, user_id)
    db.delete(db_resume)
    db.commit()

def improve_resume(
    db: Session, 
    resume_id: int, 
    user_id: int
) -> Resume:
    db_resume = get_resume(db, resume_id, user_id)
    
    original_content = db_resume.content
    improved_content = f"{original_content} [Improved]"
    
    # Save current version to history
    history_entry = ResumeHistory(
        resume_id=resume_id,
        content=original_content,
        improved_content=improved_content,
        created_at=datetime.utcnow()
    )
    db.add(history_entry)
    
    # Update resume with improved content
    db_resume.content = improved_content
    db.commit()
    db.refresh(db_resume)
    
    return db_resume

def get_resume_history(
    db: Session, 
    resume_id: int, 
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ResumeHistory]:
    # Verify the resume belongs to the user
    resume = get_resume(db, resume_id, user_id)
    if not resume:
        return []
    
    return (db.query(ResumeHistory)
             .filter(ResumeHistory.resume_id == resume_id)
             .order_by(ResumeHistory.created_at.desc())
             .offset(skip)
             .limit(limit)
             .all())
