from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.user import crud_user
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from app.core.security import create_access_token, verify_password
from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.core.config import settings
from app.crud.quiz import crud_quiz

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud_user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = await crud_user.get_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = await crud_user.create(db=db, user_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await crud_user.authenticate(db, username=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user=Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    user = await crud_user.update(db=db, db_user=current_user, user_in=user_in)
    return user


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, db: AsyncSession = Depends(get_db)):
    leaderboard = await crud_user.get_leaderboard(db, limit=limit)
    return leaderboard


@router.get("/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_active_user)
):

    stats = await crud_quiz.get_user_stats(db, current_user.id)

    return {
        "user": {
            "username": current_user.username,
            "total_score": current_user.total_score,
            "games_played": current_user.games_played,
        },
        **stats,
    }
