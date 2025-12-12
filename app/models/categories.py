from sqlalchemy import Column, Text

from app.models.base import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    category = Column(Text, nullable=False)
