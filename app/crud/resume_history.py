from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.resume import ResumeHistory
from app.schemas.resume_history import ResumeHistoryCreate

def create_resume_history(db: Session, history: ResumeHistoryCreate) -> ResumeHistory:
    """Create a new resume history entry"""
    db_history = ResumeHistory(**history.dict())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_resume_history(db: Session, resume_id: int, skip: int = 0, limit: int = 100) -> List[ResumeHistory]:
    """Get history for a specific resume"""
    return (
        db.query(ResumeHistory)
        .filter(ResumeHistory.resume_id == resume_id)
        .order_by(ResumeHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_latest_resume_history(db: Session, resume_id: int) -> Optional[ResumeHistory]:
    """Get the most recent history entry for a resume"""
    return (
        db.query(ResumeHistory)
        .filter(ResumeHistory.resume_id == resume_id)
        .order_by(ResumeHistory.created_at.desc())
        .first()
    )
