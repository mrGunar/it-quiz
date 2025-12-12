from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class UserResponse(BaseModel):
    __tablename__ = "user_responses"

    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_id = Column(Integer, ForeignKey("answers.id"))
    is_correct = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="user_responses")
    answer = relationship("Answer")
