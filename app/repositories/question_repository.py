from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import random
from app.models.answers import Answer
from app.models.quiz import DifficultyLevel
from app.models.categories import Category
from app.models.questions import Question
from app.models.user_responses import UserResponse

from app.models.user import User
from app.schemas.quiz import QuizRequest
from app.schemas.questions import QuestionCreate, QuestionUpdate
from app.repositories.base import SQLAlchemyRepository


class QuestionRepository(
    SQLAlchemyRepository[Question, QuestionCreate, QuestionUpdate]
):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Question, db_session)

    async def create(self, obj_in: QuestionCreate) -> Question:
        db_question = Question(
            question_text=obj_in.question_text,
            category=obj_in.category,
            difficulty=obj_in.difficulty,
            explanation=obj_in.explanation,
        )

        for answer_in in obj_in.answers:
            db_answer = Answer(
                answer_text=answer_in.answer_text, is_correct=answer_in.is_correct
            )
            db_question.answers.append(db_answer)

        self.db_session.add(db_question)
        await self.db_session.commit()
        await self.db_session.refresh(db_question)
        return db_question

    async def get_with_answers(self, question_id: int) -> Optional[Question]:
        result = await self.db_session.execute(
            select(Question)
            .options(selectinload(Question.answers))
            .where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_answers(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> List[Question]:
        query = select(Question).options(selectinload(Question.answers))

        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(Question, field) == value)

        query = query.offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_random_questions(
        self,
        category: Optional[Category] = None,
        difficulty: Optional[DifficultyLevel] = None,
        limit: int = 10,
    ) -> List[Question]:
        query = select(Question).options(selectinload(Question.answers))

        if category:
            query = query.where(Question.category == category)
        if difficulty:
            query = query.where(Question.difficulty == difficulty)

        result = await self.db_session.execute(query)
        all_questions = result.scalars().all()

        selected_questions = random.sample(
            all_questions, min(limit, len(all_questions))
        )

        for question in selected_questions:
            random.shuffle(question.answers)

        return selected_questions

    async def get_correct_answer(self, question_id: int) -> Optional[Answer]:
        result = await self.db_session.execute(
            select(Answer).where(
                and_(Answer.question_id == question_id, Answer.is_correct == True)
            )
        )
        return result.scalar_one_or_none()
