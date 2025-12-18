from fastapi import APIRouter, Depends, HTTPException, status

from app.services.category_service import CategoryService
from app.api.dependencies import get_category_service
from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse
from app.middleware.logger import logger

router = APIRouter()


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all categories",
    description="Retrieve all available categories from the system",
)
async def get(
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponse]:
    """
    Get all available categories.

    Returns:
        List[CategoryResponse]: List of all categories.
    """
    try:
        logger.info("Fetching all categories.")
        categories = await service.get()
        logger.info(f"Successfully retrieved {len(categories)} categories")
        return categories
    except ValueError as e:
        logger.error("Failed to retrieve categories.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error while retrieving categories.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID",
    description="Retrieve a specific category by its ID",
)
async def get(
    category_id: int, service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    """Get a category by ID.

    Args:
        category_id: The ID of the category to retrieve.

    Returns:
        CategoryResponse: The requested category.

    Raises:
        HTTPException: 404 if category is not found.

    """
    logger.info(f"Fetching category with ID: {category_id}")

    try:
        category = await service.get_by_id(category_id)

        if category is None:
            logger.warning(f"Category not found with ID: {category_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found",
            )

        logger.info(f"Successfully retrieved category with ID: {category_id}")
        return category

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error while retrieving category with ID: {category_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new category",
    description="Create a new category in the system",
)
async def create(
    category_in: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Create a new category.

    Args:
        category_in: The category data to create.

    Returns:
        CategoryResponse: The newly created category.

    Raises:
        HTTPException: 500 if a category is not created.
    """
    logger.info("Creating a new category.")

    try:
        new_category = await service.create(category_in)
        logger.info("Category created successfully.")
        return new_category

    except Exception as err:

        logger.error(f"Failed to create category: {err}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        )


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update category",
    description="Update an existing category by ID",
)
async def update(
    category_id: int,
    category_in: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Update the category by ID.

    Args:
        category_id: The ID of the category to update
        category_in: The updated category data

    Returns:
        CategoryResponse: The updated category

    Raises:
        HTTPException: 404 if category is not found
    """
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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Delete a category by ID",
)
async def delete(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
) -> None:
    """
    Delete a category by ID.

    Args:
        category_id: The ID of the category to delete

    Raises:
        HTTPException: 404 if category is not found
    """
    deleted = await service.delete(category_id)
    logger.info("A category has been deleted successfully.")
    if not deleted:
        logger.error(
            f"Failed to delete a category by id: `{category_id}`. Category not found."
        )
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
