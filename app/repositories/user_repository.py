from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import SQLAlchemyRepository
from app.core.security import get_password_hash, verify_password


class UserRepository(SQLAlchemyRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def create(self, user: UserCreate) -> User:

        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )
        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db_session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db_session.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db_session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_score(self, user_id: int, score: int) -> Optional[User]:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                total_score=User.total_score + score, games_played=User.games_played + 1
            )
            .returning(User)
        )

        result = await self.db_session.execute(stmt)
        await self.db_session.commit()

        updated_user = result.scalar_one_or_none()
        if updated_user:
            await self.db_session.refresh(updated_user)

        return updated_user

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = (
            select(
                User.username,
                User.total_score,
                User.games_played,
                func.coalesce(
                    func.round(User.total_score * 1.0 / User.games_played, 2), 0
                ).label("avg_score"),
            )
            .where(User.games_played > 0)
            .order_by(User.total_score.desc())
            .limit(limit)
        )

        result = await self.db_session.execute(query)
        rows = result.all()

        return [
            {
                "username": row.username,
                "total_score": row.total_score,
                "games_played": row.games_played,
                "avg_score": row.avg_score,
            }
            for row in rows
        ]

    async def update(self, id: int, user: UserUpdate) -> Optional[User]:
        updated_user = user.model_dump(exclude_unset=True)

        if updated_user.get("password"):
            updated_user["hashed_password"] = get_password_hash(
                updated_user.pop("password")
            )

        stmt = update(User).where(User.id == id).values(**updated_user).returning(User)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()

        updated_user = result.scalar_one_or_none()
        if updated_user:
            await self.db_session.refresh(updated_user)

        return updated_user
