from fastapi import APIRouter, Depends, HTTPException, status
from app.services.answer_service import AnswerService
from app.api.dependencies import get_answer_service

router = APIRouter()


@router.get("/answers")
async def get_answers(service: AnswerService = Depends(get_answer_service)):
    answers = await service.get_answers()
    return answers
