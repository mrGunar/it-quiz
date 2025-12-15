from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.models.categories import Category

from app.repositories.base import SQLAlchemyRepository


class CategoryRepository(SQLAlchemyRepository[Category, dict, dict]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Category, db_session)

    async def get_categories(self) -> list[Category]:
        result = await self.db_session.execute(select(Category))
        return result.scalars().all()
