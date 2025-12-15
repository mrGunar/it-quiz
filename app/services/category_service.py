from typing import List

from app.repositories import RepositoryFactory


class CategoryService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def get_categories(
        self,
    ) -> List:

        return await self.repo_factory.categories.get_categories()
