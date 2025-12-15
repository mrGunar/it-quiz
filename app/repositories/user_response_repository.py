from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer, select, func, and_
from sqlalchemy.orm import selectinload
import random
from app.models.answers import Answer
from app.models.quiz import DifficultyLevel
from app.models.categories import Category
from app.models.questions import Question
from app.models.user_responses import UserResponse

from app.models.user import User
from app.schemas.questions import QuestionCreate, QuestionUpdate
from app.schemas.quiz import QuizRequest
from app.repositories.base import SQLAlchemyRepository


class UserResponseRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.model = UserResponse

    async def create(
        self, user_id: int, question_id: int, answer_id: int, is_correct: bool
    ) -> UserResponse:
        db_response = UserResponse(
            user_id=user_id,
            question_id=question_id,
            answer_id=answer_id,
            is_correct=is_correct,
        )
        self.db_session.add(db_response)
        await self.db_session.commit()
        await self.db_session.refresh(db_response)
        return db_response

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        total_query = select(func.count(UserResponse.id)).where(
            UserResponse.user_id == user_id
        )
        total_result = await self.db_session.execute(total_query)
        total_answers = total_result.scalar() or 0

        correct_query = select(func.count(UserResponse.id)).where(
            and_(UserResponse.user_id == user_id, UserResponse.is_correct == True)
        )
        correct_result = await self.db_session.execute(correct_query)
        correct_answers = correct_result.scalar() or 0

        category_query = (
            select(
                Question.category,
                func.count(UserResponse.id).label("total"),
                func.sum(func.cast(UserResponse.is_correct, Integer)).label("correct"),
            )
            .join(Question, UserResponse.question_id == Question.id)
            .where(UserResponse.user_id == user_id)
            .group_by(Question.category)
        )
        category_result = await self.db_session.execute(category_query)

        by_category = {}
        for row in category_result:
            by_category[row.category.value] = {
                "total": row.total,
                "correct": row.correct or 0,
                "accuracy": (
                    (row.correct or 0) / row.total * 100 if row.total > 0 else 0
                ),
            }

        difficulty_query = (
            select(
                Question.difficulty,
                func.count(UserResponse.id).label("total"),
                func.sum(func.cast(UserResponse.is_correct, Integer)).label("correct"),
            )
            .join(Question, UserResponse.question_id == Question.id)
            .where(UserResponse.user_id == user_id)
            .group_by(Question.difficulty)
        )
        difficulty_result = await self.db_session.execute(difficulty_query)

        by_difficulty = {}
        for row in difficulty_result:
            by_difficulty[row.difficulty.value] = {
                "total": row.total,
                "correct": row.correct or 0,
                "accuracy": (
                    (row.correct or 0) / row.total * 100 if row.total > 0 else 0
                ),
            }

        return {
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "accuracy": (
                (correct_answers / total_answers * 100) if total_answers > 0 else 0
            ),
            "by_category": by_category,
            "by_difficulty": by_difficulty,
        }

    async def get_user_responses(
        self, user_id: int, limit: int = 100
    ) -> List[UserResponse]:
        result = await self.db_session.execute(
            select(UserResponse)
            .where(UserResponse.user_id == user_id)
            .order_by(UserResponse.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
