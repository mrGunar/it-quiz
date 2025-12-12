from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    total_score = Column(Integer, default=0)
    games_played = Column(Integer, default=0)

    responses = relationship("UserResponse", back_populates="user")
