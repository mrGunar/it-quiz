from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_quiz_service
from app.schemas.quiz import (
    QuizRequest,
    QuizSubmit,
    QuizResponse,
)
from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.middleware.logger import logger
from app.services.quiz_service import QuizService

router = APIRouter()


@router.post("/quiz/generate")
async def generate_quiz(
    quiz_request: QuizRequest,
    quiz_service: QuizService = Depends(get_quiz_service),
    current_user: User = Depends(get_current_active_user),
):
    questions = await quiz_service.generate_quiz(quiz_request)
    return questions


@router.post("/quiz/submit", response_model=QuizResponse)
async def submit_quiz(
    quiz_submit: QuizSubmit,
    quiz_service: QuizService = Depends(get_quiz_service),
    current_user: User = Depends(get_current_active_user),
):
    result = await quiz_service.submit_quiz(current_user.id, quiz_submit)
    return result
