from pydantic import BaseModel, ConfigDict

from typing import Optional
from datetime import datetime

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
    category_id: Optional[int] = None


class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionsListResponse(BaseModel):
    items: list[QuestionResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
