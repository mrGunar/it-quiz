from fastapi import APIRouter, Depends, HTTPException, status
from app.services.category_service import CategoryService
from app.api.dependencies import get_category_service

router = APIRouter()


@router.get("/categories")
async def get_categories(service: CategoryService = Depends(get_category_service)):
    categories = await service.get_categories()
    return categories
