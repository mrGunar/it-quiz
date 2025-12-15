from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_difficulty_service
from app.services.quiz_service import QuizService

router = APIRouter()


@router.get("/difficulties")
async def get_difficulties(quiz_service: QuizService = Depends(get_difficulty_service)):
    difficulties = await quiz_service.get_difficulties()
    return difficulties
