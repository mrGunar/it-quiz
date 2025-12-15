from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.answer_repository import AnswerRepository
from app.repositories.user_response_repository import UserResponseRepository
from app.repositories.category_repository import CategoryRepository


class RepositoryFactory:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @property
    def users(self) -> UserRepository:
        return UserRepository(self.db_session)

    @property
    def questions(self) -> QuestionRepository:
        return QuestionRepository(self.db_session)

    @property
    def answers(self) -> AnswerRepository:
        return AnswerRepository(self.db_session)

    @property
    def user_responses(self) -> UserResponseRepository:
        return UserResponseRepository(self.db_session)

    @property
    def categories(self) -> CategoryRepository:
        return CategoryRepository(self.db_session)
