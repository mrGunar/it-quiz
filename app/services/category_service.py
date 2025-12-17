from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.repositories import RepositoryFactory
from app.models.categories import Category


class CategoryService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def get(self) -> list[Category]:
        return await self.repo_factory.categories.get_categories()

    async def get_by_id(self, category_id: int) -> Category:
        return await self.repo_factory.categories.get(category_id)

    async def create(self, category: CategoryCreate) -> Category:
        return await self.repo_factory.categories.create(category)

    async def update(self, category_id: int, category: CategoryUpdate) -> Category:
        return await self.repo_factory.categories.update(category_id, category)

    async def delete(self, category_id: int) -> bool:
        return await self.repo_factory.categories.delete(category_id)
