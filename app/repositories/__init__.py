from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository


class RepositoryFactory:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @property
    def users(self) -> UserRepository:
        return UserRepository(self.db_session)

    # @property
    # def questions(self) -> QuestionRepository:
    #     return QuestionRepository(self.db_session)

    # @property
    # def answers(self) -> AnswerRepository:
    #     return AnswerRepository(self.db_session)

    # @property
    # def user_responses(self) -> UserResponseRepository:
    #     return UserResponseRepository(self.db_session)
