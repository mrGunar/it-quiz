from app.models.quiz import DifficultyLevel
from app.repositories import RepositoryFactory


class DifficultyService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def get_difficulties(self) -> list[str]:
        return [difficulty.value for difficulty in DifficultyLevel]
