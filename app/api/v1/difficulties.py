from fastapi import APIRouter, Depends

from app.api.dependencies import get_difficulty_service
from app.services.difficulty_service import DifficultyService
from app.middleware.logger import logger

router = APIRouter()


@router.get("/difficulties", response_model=list[str])
async def get_difficulties(
    service: DifficultyService = Depends(get_difficulty_service),
):
    difficulties = await service.get_difficulties()
    logger.info(f"All difficulties retrieved. Count: {len(difficulties)}")
    return difficulties
