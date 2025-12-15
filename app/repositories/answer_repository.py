from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.answers import Answer
from app.repositories.base import SQLAlchemyRepository


class AnswerRepository(SQLAlchemyRepository[Answer, dict, dict]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Answer, db_session)

    async def get_by_question(self, question_id: int) -> list[Answer]:
        result = await self.db_session.execute(
            select(Answer).where(Answer.question_id == question_id)
        )
        return result.scalars().all()
