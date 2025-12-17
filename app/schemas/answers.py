from datetime import datetime

from pydantic import BaseModel


class AnswerBase(BaseModel):
    answer_text: str
    is_correct: bool
    question_id: int


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(AnswerBase):
    answer_text: str | None = None
    is_correct: bool | None = None
    question_id: int | None = None


class AnswerResponse(AnswerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
