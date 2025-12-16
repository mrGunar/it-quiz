from fastapi import APIRouter, Depends, HTTPException, status

from app.services.category_service import CategoryService
from app.api.dependencies import get_category_service
from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse
from app.middleware.logger import logger

router = APIRouter()


@router.get("/categories")
async def get_categories(service: CategoryService = Depends(get_category_service)):
    try:
        category = await service.get_categories()
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_in: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        new_category = await service.create_category(category_in)
        return new_category
    except Exception as err:
        logger.error(f"There is an error during creating.")
        raise HTTPException(status_code=err.status_code, detail=err.message)
