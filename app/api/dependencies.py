from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.user import crud_user
from app.core.config import settings
from app.repositories import RepositoryFactory
from app.services.user_service import UserService

security = HTTPBearer()


def get_repository_factory(db: AsyncSession = Depends(get_db)) -> RepositoryFactory:
    return RepositoryFactory(db)


def get_user_service(
    repo_factory: RepositoryFactory = Depends(get_repository_factory),
) -> UserService:
    return UserService(repo_factory)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(current_user=Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
