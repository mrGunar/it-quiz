from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from app.core.security import create_access_token, verify_password
from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.core.config import settings
from app.api.dependencies import (
    get_current_active_user,
    get_user_service,
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.register_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.authenticate_user(
        username=form_data.username, password=form_data.password
    )

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


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user=Depends(get_current_active_user),
):
    user = await user_service.update_user(current_user.id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10, user_service: UserService = Depends(get_user_service)
):
    leaderboard = await user_service.get_leaderboard(limit)
    return leaderboard


@router.get("/stats")
async def get_user_stats(
    user_service: UserService = Depends(get_user_service),
    current_user=Depends(get_current_active_user),
):
    stats = await user_service.get_user_stats(current_user.id)
    return stats
