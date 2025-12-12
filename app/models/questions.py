from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.quiz import DifficultyLevel


class Question(BaseModel):
    __tablename__ = "questions"

    question_text = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    explanation = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))

    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    user_responses = relationship(
        "UserResponse", back_populates="question", cascade="all, delete-orphan"
    )
