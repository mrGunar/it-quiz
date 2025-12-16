from pydantic import BaseModel

from typing import List, Optional
from datetime import datetime

from app.schemas.answers import AnswerCreate, AnswerResponse
from app.models.quiz import DifficultyLevel


class QuestionBase(BaseModel):
    question_text: str
    difficulty: DifficultyLevel
    explanation: Optional[str] = None


class QuestionCreate(QuestionBase):
    category: int


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    explanation: Optional[str] = None
    category: Optional[int] = None


class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
