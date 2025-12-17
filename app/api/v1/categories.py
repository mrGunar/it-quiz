from fastapi import APIRouter, Depends, HTTPException

from app.services.category_service import CategoryService
from app.api.dependencies import get_category_service
from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse
from app.middleware.logger import logger

router = APIRouter()


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    status_code=200,
)
async def get(service: CategoryService = Depends(get_category_service)):
    """Get all available categories."""
    try:
        categories = await service.get()
        logger.info(
            f"Categories retrieved. Count: {len(categories)}",
        )
        return categories
    except ValueError as e:
        logger.error("Failed to retrieve categories.")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    status_code=200,
)
async def get(
    category_id: int, service: CategoryService = Depends(get_category_service)
):
    """Get a category by id."""
    category = await service.get_by_id(category_id)
    if category is None:
        logger.error("Failed to retrieve categories. Category not found.")
        raise HTTPException(status_code=404, detail="Category not found.")
    return category


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=201,
)
async def create(
    category_in: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    """Create a new category."""
    try:
        new_category = await service.create(category_in)
        logger.info("A new category has been created successfully.")
        return new_category
    except Exception as err:
        logger.error(err.message)
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    status_code=200,
)
async def update(
    category_id: int,
    category_in: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    """Update the category by id."""
    category = await service.update(category_id, category_in)
    logger.info("A category has been updated successfully.")
    if category is None:
        logger.error(
            f"Failed to update a category by id: `{category_id}`. Category not found."
        )
        raise HTTPException(status_code=400, detail="Category not found")
    return category


@router.delete(
    "/categories/{category_id}",
    status_code=204,
)
async def delete(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    """Delete a category by id."""
    deleted = await service.delete(category_id)
    logger.info("A category has been deleted successfully.")
    if not deleted:
        logger.error(
            f"Failed to delete a category by id: `{category_id}`. Category not found."
        )
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
