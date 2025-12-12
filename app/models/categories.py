from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    category = Column(Text, nullable=False)

    questions = relationship(
        "Question",
        back_populates="categories",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
