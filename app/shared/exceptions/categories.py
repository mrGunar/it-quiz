from fastapi import HTTPException
from fastapi import status


class CategoryNotFoundError(HTTPException):
    def __init__(self, category_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )


class CategoryAlreadyExistsError(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name '{name}' already exists",
        )
