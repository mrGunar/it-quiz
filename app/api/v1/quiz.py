from fastapi import APIRouter, Depends

from app.api.dependencies import get_quiz_service
from app.schemas.quiz import (
    QuizRequest,
    QuizSubmit,
    QuizResponse,
)
from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.services.quiz_service import QuizService

router = APIRouter()


@router.post("/generate")
async def generate_quiz(
    quiz_request: QuizRequest,
    service: QuizService = Depends(get_quiz_service),
    # TODO: tmp comment this line
    # current_user: User = Depends(get_current_active_user),
):
    questions = await service.generate_quiz(quiz_request)
    return questions


@router.post("/submit", response_model=QuizResponse)
async def submit_quiz(
    quiz_submit: QuizSubmit,
    service: QuizService = Depends(get_quiz_service),
    current_user: User = Depends(get_current_active_user),
):
    result = await service.submit_quiz(current_user.id, quiz_submit)
    return result
