from datetime import datetime

from pydantic import BaseModel


class AnswerBase(BaseModel):
    answer_text: str
    is_correct: bool


class AnswerCreate(AnswerBase):
    pass


class AnswerResponse(AnswerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
