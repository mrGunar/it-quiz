from typing import List

from app.schemas.categories import CategoryCreate
from app.repositories import RepositoryFactory


class CategoryService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def get_categories(
        self,
    ) -> List[str]:

        return await self.repo_factory.categories.get_categories()

    async def create_category(self, category: CategoryCreate):
        return await self.repo_factory.categories.create(category)
