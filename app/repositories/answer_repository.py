from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.answers import Answer
from app.repositories.base import SQLAlchemyRepository
from app.schemas.answers import AnswerCreate, AnswerUpdate
from app.shared.exceptions.database import DatabaseException


class AnswerRepository(SQLAlchemyRepository[Answer, AnswerCreate, AnswerUpdate]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Answer, db_session)

    async def get_by_question_id(self, question_id: int) -> list[Answer]:
        result = await self.db_session.execute(
            select(Answer).where(Answer.question_id == question_id)
        )
        return result.scalars().all()

    async def create_answer(
        self,
        question_id: int,
        obj_in: AnswerCreate,
    ) -> Answer:
        current_answers = await self.get_by_question_id(question_id)
        correct_answers = (
            sum([answer.is_correct for answer in current_answers]) + obj_in.is_correct
        )

        if correct_answers > 1:
            raise DatabaseException(
                message="More than 1 correct answers.", status_code=409
            )

        db_obj = self.model(**obj_in.dict(), question_id=question_id)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj
