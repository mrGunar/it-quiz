from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    total_score: int
    games_played: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
