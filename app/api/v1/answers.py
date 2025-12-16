from fastapi import APIRouter, Depends, HTTPException, status
from app.services.answer_service import AnswerService
from app.api.dependencies import get_answer_service
from app.schemas.answers import AnswerCreate

router = APIRouter()


@router.get("/answers")
async def get_answers_for_question_by_id(
    question_id: int,
    service: AnswerService = Depends(get_answer_service),
):
    answers = await service.get_for_question_by_id(question_id)
    return answers


@router.post("/answers")
async def create_answer_for_question(
    question_id: int,
    answer_in: AnswerCreate,
    service: AnswerService = Depends(get_answer_service),
):
    try:
        answers = await service.create_for_question(question_id, answer_in)
        return answers
    except Exception as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
