from typing import List

from app.repositories import RepositoryFactory


class AnswerService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def get_answers(
        self,
    ) -> List[str]:

        return ["lol", "kek"]
