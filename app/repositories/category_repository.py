from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.categories import Category
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.repositories.base import SQLAlchemyRepository
from app.shared.exceptions.database import parse_error_message


class CategoryRepository(
    SQLAlchemyRepository[Category, CategoryCreate, CategoryUpdate]
):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Category, db_session)

    async def get_categories(self) -> list[Category]:
        result = await self.db_session.execute(select(Category))
        return result.scalars().all()

    async def create(self, category: CategoryCreate) -> Category:
        try:
            new_category = Category(category=category.category)
            self.db_session.add(new_category)
            await self.db_session.commit()
            await self.db_session.refresh(new_category)
            return new_category
        except IntegrityError as e:
            await self.db_session.rollback()
            error = parse_error_message(e)
            raise error
