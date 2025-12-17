from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.answers import Answer
from app.repositories.base import SQLAlchemyRepository
from app.schemas.answers import AnswerCreate, AnswerUpdate
from app.shared.exceptions.database import DatabaseException, parse_error_message


class AnswerRepository(SQLAlchemyRepository[Answer, AnswerCreate, AnswerUpdate]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Answer, db_session)

    async def get_by_question_id(self, question_id: int) -> list[Answer]:
        result = await self.db_session.execute(
            select(Answer).where(Answer.question_id == question_id)
        )
        return result.scalars().all()

    async def count_true_answer_for_question(self, question_id: int) -> int:
        current_answers = await self.get_by_question_id(question_id)
        return sum([answer.is_correct for answer in current_answers])

    async def create(
        self,
        obj_in: AnswerCreate,
    ) -> Answer:

        correct_answers = (
            await self.count_true_answer_for_question(obj_in.question_id)
            + obj_in.is_correct
        )

        if correct_answers > 1:
            raise DatabaseException(
                message="More than 1 correct answers.", status_code=409
            )

        try:
            db_obj = self.model(**obj_in.model_dump())
            self.db_session.add(db_obj)
            await self.db_session.commit()
            await self.db_session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.db_session.rollback()
            error = parse_error_message(e)
            raise error

    async def update(self, id: int, obj_in: AnswerUpdate) -> Answer:
        correct_answers = (
            await self.count_true_answer_for_question(obj_in.question_id)
            + obj_in.is_correct
        )
        if correct_answers > 1:
            raise DatabaseException(
                message="More than 1 correct answers.", status_code=409
            )
        return await super().update(id, obj_in)
