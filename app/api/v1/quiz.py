from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.quiz import crud_quiz
from app.schemas.quiz import (
    QuizRequest,
    QuizSubmit,
    QuizResponse,
)
from app.schemas.questions import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.crud.user import crud_user
from app.models.quiz import DifficultyLevel
from app.models.categories import Category
from app.middleware.logger import logger

router = APIRouter()


@router.post("/questions/", response_model=QuestionResponse)
async def create_question(
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a question."""
    correct_answers = [a for a in question_in.answers if a.is_correct]
    if len(correct_answers) != 1:

        raise HTTPException(
            status_code=400, detail="Question must have exactly one correct answer"
        )

    question = await crud_quiz.create_question(db, question_in)
    return question


@router.get("/questions/", response_model=List[QuestionResponse])
async def read_questions(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    difficulty: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    questions = await crud_quiz.get_questions(
        db, skip=skip, limit=limit, category=category, difficulty=difficulty
    )
    return questions


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def read_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    question = await crud_quiz.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_in: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    question = await crud_quiz.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    for field, value in question_in.model_dump(exclude_unset=True).items():
        setattr(question, field, value)

    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    question = await crud_quiz.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    await db.delete(question)
    await db.commit()
    return {"message": "Question deleted successfully"}


@router.post("/quiz/generate")
async def generate_quiz(
    quiz_request: QuizRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    questions = await crud_quiz.generate_quiz(db, quiz_request)

    formatted_questions = []
    for q in questions:
        formatted_questions.append(
            {
                "id": q.id,
                "question_text": q.question_text,
                "category": q.category.value,
                "difficulty": q.difficulty.value,
                "answers": [
                    {"id": a.id, "answer_text": a.answer_text} for a in q.answers
                ],
            }
        )

    return formatted_questions


@router.post("/quiz/submit", response_model=QuizResponse)
async def submit_quiz(
    quiz_submit: QuizSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    answers = [
        {"question_id": a.question_id, "answer_id": a.answer_id}
        for a in quiz_submit.answers
    ]

    result = await crud_quiz.submit_quiz(db, current_user.id, answers)

    await crud_user.update_score(db, current_user.id, result["score"])

    return result


@router.get("/categories")
async def get_categories():
    return [category.value for category in Category]


@router.get("/difficulties")
async def get_difficulties():
    logger.info("All difficulties have been obtained.")
    return [difficulty.value for difficulty in DifficultyLevel]
