from fastapi import APIRouter
from app.api.v1 import user, quiz

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
