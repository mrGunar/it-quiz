from typing import List

from app.repositories import RepositoryFactory
from app.schemas.answers import AnswerCreate


class AnswerService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def get_for_question_by_id(
        self,
        question_id: int,
    ) -> List[str]:

        return await self.repo_factory.answers.get_by_question_id(question_id)

    async def create_for_question(
        self,
        question_id: int,
        answer_in: AnswerCreate,
    ) -> List[str]:
        return await self.repo_factory.answers.create_answer(question_id, answer_in)
