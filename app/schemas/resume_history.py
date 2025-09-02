from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ResumeHistoryBase(BaseModel):
    content: str
    improved_content: Optional[str] = None
    created_at: datetime

class ResumeHistoryCreate(ResumeHistoryBase):
    resume_id: int

class ResumeHistoryInDBBase(ResumeHistoryBase):
    id: int
    resume_id: int
    
    class Config:
        orm_mode = True

class ResumeHistory(ResumeHistoryInDBBase):
    pass
