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
    answers: List[AnswerCreate]


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    explanation: Optional[str] = None


class QuestionResponse(QuestionBase):
    id: int
    answers: List[AnswerResponse]
    created_at: datetime

    class Config:
        from_attributes = True
