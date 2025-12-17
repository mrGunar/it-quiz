from app.repositories import RepositoryFactory
from app.schemas.answers import AnswerCreate, AnswerUpdate

from app.models.answers import Answer


class AnswerService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def get_for_question_by_id(
        self,
        question_id: int,
    ) -> list[Answer]:
        return await self.repo_factory.answers.get_by_question_id(question_id)

    async def create_for_question(
        self,
        answer_in: AnswerCreate,
    ) -> Answer:
        return await self.repo_factory.answers.create(answer_in)

    async def update(self, answer_id: int, answer: AnswerUpdate) -> Answer:
        return await self.repo_factory.answers.update(answer_id, answer)

    async def delete(self, answer_id: int) -> bool:
        return await self.repo_factory.answers.delete(answer_id)
