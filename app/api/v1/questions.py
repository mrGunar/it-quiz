from fastapi import APIRouter, Depends, HTTPException

from app.schemas.questions import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
from app.api.dependencies import (
    get_current_active_user,
    get_current_admin_user,
    get_question_service,
)
from app.services.question_service import QuestionService
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=QuestionResponse)
async def create_question(
    question_in: QuestionCreate,
    service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_admin_user),
):
    try:
        question = await service.create_question(question_in)
        return question
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[QuestionResponse])
async def read_questions(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    difficulty: str = None,
    service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_active_user),
):
    questions = await service.get_questions(
        skip=skip, limit=limit, category=category, difficulty=difficulty
    )
    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
async def read_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_active_user),
):
    question = await service.get_question(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_in: QuestionUpdate,
    service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_admin_user),
):
    question = await service.update_question(question_id, question_in)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_admin_user),
):
    deleted = await service.delete_question(question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}
