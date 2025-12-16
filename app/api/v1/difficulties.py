from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_difficulty_service
from app.services.difficulty_service import DifficultyService

router = APIRouter()


@router.get("/difficulties")
async def get_difficulties(
    service: DifficultyService = Depends(get_difficulty_service),
):
    difficulties = await service.get_difficulties()
    return difficulties
