from typing import Any

from app.repositories import RepositoryFactory
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User


class UserService:
    def __init__(self, repository_factory: RepositoryFactory) -> None:
        self.repo_factory = repository_factory

    async def register_user(self, user_in: UserCreate) -> User:
        if await self.repo_factory.users.get_by_email(user_in.email):
            raise ValueError("Email already registered.")

        if await self.repo_factory.users.get_by_username(user_in.username):
            raise ValueError("Username already exists.")

        return await self.repo_factory.users.create(user_in)

    async def authenticate_user(self, username: str, password: str) -> User | None:
        return await self.repo_factory.users.authenticate(username, password)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repo_factory.users.get(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        return await self.repo_factory.users.get_by_username(username)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repo_factory.users.get_by_email(email)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User | None:
        return await self.repo_factory.users.update(user_id, user_in)

    async def update_user_score(self, user_id: int, score: int) -> User | None:
        return await self.repo_factory.users.update_score(user_id, score)

    async def get_leaderboard(self, limit: int = 10) -> list[dict[str, Any]]:
        return await self.repo_factory.users.get_leaderboard(limit)

    async def get_user_stats(self, user_id: int) -> dict[str, Any]:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        stats = await self.repo_factory.user_responses.get_user_stats(user_id)

        return {
            "user": {
                "username": user.username,
                "total_score": user.total_score,
                "games_played": user.games_played,
            },
            **stats,
        }
