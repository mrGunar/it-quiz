from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import ValidationError

from app.services.category_service import CategoryService
from app.api.dependencies import get_category_service
from app.schemas.categories import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)
from app.middleware.logger import logger
from app.shared.exceptions.categories import (
    CategoryNotFoundError,
    CategoryAlreadyExistsError,
)

router = APIRouter()


@router.get(
    "/",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get categories",
    description="Retrieve categories with optional pagination and filtering",
    responses={
        200: {"description": "Categories retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        500: {"description": "Internal server error"},
    },
)
async def get(
    skip: int = Query(
        default=0, ge=0, description="Number of records to skip (for pagination)"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
        description="Maximum number of records to return (max: 500)",
    ),
    name: str | None = Query(
        default=None,
        description="Filter by category name (case-insensitive partial match)",
    ),
    service: CategoryService = Depends(get_category_service),
) -> CategoryListResponse:
    """Get all available categories."""
    try:
        logger.info(
            f"Fetching categories with filters: skip={skip}, limit={limit}, "
            f"name={name}"
        )

        categories = await service.get_all(
            skip=skip,
            limit=limit,
            name=name,
        )

        total_count = len(categories)

        logger.info(
            f"Successfully retrieved {len(categories)} of {total_count} categories"
        )

        return CategoryListResponse(
            items=categories,
            total=total_count,
            skip=skip,
            limit=limit,
        )
    except ValueError as e:
        logger.error(f"Invalid request parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while retrieving categories: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve categories. Please try again later.",
        )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID",
    description="Retrieve a specific category by its ID",
)
async def get(
    category_id: int = Path(
        ..., ge=1, description="Category ID (must be positive integer)"
    ),
    service: CategoryService = Depends(get_category_service),
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
            raise CategoryNotFoundError(category_id)

        logger.info(f"Successfully retrieved category with ID: {category_id}")
        return category

    except CategoryNotFoundError:
        raise
    except ValueError as e:
        logger.error(f"Invalid category ID format: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid category ID: {str(e)}",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while retrieving category with ID: {category_id} - {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve category. Please try again later.",
        )


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new category",
    description="Create a new category",
    responses={
        201: {"description": "Category created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Category with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
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
    logger.info(f"Creating a new category with name: {category_in.name}")

    try:
        existing_category = await service.get_by_name(category_in.name)
        if existing_category:
            logger.warning(f"Category already exists with name: {category_in.name}")
            raise CategoryAlreadyExistsError(category_in.name)

        new_category = await service.create(category_in)

        logger.info(f"Category created successfully with ID: {new_category.id}")
        return new_category

    except CategoryAlreadyExistsError:
        raise
    except ValidationError as e:
        logger.error(f"Validation error while creating category: {e.errors()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=e.errors(),
        )
    except ValueError as e:
        logger.error(f"Invalid category data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to create category: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create category. Please try again later.",
        )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update category",
    description="Update an existing category by ID",
    responses={
        200: {"description": "Category updated successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "Category not found"},
        409: {"description": "Category with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update(
    category_id: int = Path(
        ...,
        ge=1,
        description="Category ID to update",
    ),
    category_in: CategoryUpdate = None,
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
    logger.info(f"Updating category with ID: {category_id}")

    try:
        existing_category = await service.get_by_id(category_id)
        if not existing_category:
            logger.warning(f"Category not found with ID: {category_id}")
            raise CategoryNotFoundError(category_id)

        updated_category = await service.update(category_id, category_in)

        if updated_category is None:
            logger.error(f"Failed to update category with ID: {category_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update category",
            )

        logger.info(f"Category updated successfully with ID: {category_id}")
        return updated_category

    except (CategoryNotFoundError, CategoryAlreadyExistsError):
        raise
    except ValidationError as e:
        logger.error(f"Validation error while updating category: {e.errors()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=e.errors(),
        )
    except ValueError as e:
        logger.error(f"Invalid update data for category ID {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while updating category with ID {category_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update category. Please try again later.",
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Delete a category by ID",
    responses={
        204: {"description": "Category deleted successfully"},
        404: {"description": "Category not found"},
        409: {
            "description": "Category cannot be deleted (e.g., has associated questions)"
        },
        422: {"description": "Invalid category ID format"},
        500: {"description": "Internal server error"},
    },
)
async def delete(
    category_id: int = Path(
        ...,
        ge=1,
        description="Category ID to delete",
    ),
    service: CategoryService = Depends(get_category_service),
) -> None:
    """
    Delete a category by ID.

    Args:
        category_id: The ID of the category to delete

    Raises:
        HTTPException: 404 if category is not found
    """
    logger.info(f"Deleting category with ID: {category_id}")

    try:
        category = await service.get_by_id(category_id)
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            raise CategoryNotFoundError(category_id)

        deleted = await service.delete(category_id)

        if not deleted:
            logger.error(f"Failed to delete category with ID: {category_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete category",
            )

        logger.info(f"Category deleted successfully with ID: {category_id}")

    except (CategoryNotFoundError, HTTPException):
        raise
    except ValueError as e:
        logger.error(f"Invalid category ID format: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid category ID: {str(e)}",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while deleting category with ID {category_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete category. Please try again later.",
        )
