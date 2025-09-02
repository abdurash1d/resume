from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, ForwardRef, Any

class ResumeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=10)

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=10)

class ResumeInDB(ResumeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResumeHistoryBase(BaseModel):
    id: int
    resume_id: int
    content: str
    improved_content: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# Forward reference for Resume model
class Resume(ResumeInDB):
    history: List[Any] = []
    
    class Config:
        from_attributes = True

class ResumeHistory(ResumeHistoryBase):
    resume: Resume
    
    class Config:
        orm_mode = True

class ResumeWithHistory(ResumeInDB):
    history: List[ResumeHistory] = []
    improved_content: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeImprove(BaseModel):
    content: str
