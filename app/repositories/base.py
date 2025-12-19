from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import func


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: DeclarativeMeta, db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        pass

    @abstractmethod
    async def get(self, id: int) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def get_multi(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> List[ModelType]:
        pass

    @abstractmethod
    async def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass


class SQLAlchemyRepository(
    BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> List[ModelType]:
        query = select(self.model)

        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        update_data = obj_in.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get(id)

        # TODO: FK constraint by category_id
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )

        result = await self.db_session.execute(stmt)
        await self.db_session.commit()

        updated_obj = result.scalar_one_or_none()
        if updated_obj:
            await self.db_session.refresh(updated_obj)

        return updated_obj

    async def delete(self, id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.rowcount > 0

    async def count(self, **filters) -> int:
        query = select(func.count()).select_from(self.model)

        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, field) == value)

        result = await self.db_session.execute(query)
        return result.scalar()

    async def exists(self, **filters) -> bool:
        query = select(self.model).limit(1)

        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, field) == value)

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none() is not None
