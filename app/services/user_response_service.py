from typing import List

from app.repositories import RepositoryFactory


class UserResponseService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def foo(
        self,
    ) -> List[str]:

        return ["Foo", "Bar"]
