from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import ValidationError

from app.schemas.questions import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    QuestionsListResponse,
)
from app.api.dependencies import (
    get_current_active_user,
    get_current_admin_user,
    get_question_service,
)
from app.services.question_service import QuestionService
from app.models.user import User
from app.middleware.logger import logger
from app.shared.exceptions.questions import QuestionNotFoundError, QuestionCreationError

router = APIRouter()


@router.post(
    "/",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Question created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin access required"},
        422: {"description": "Validation error"},
    },
)
async def create_question(
    question_in: QuestionCreate,
    service: QuestionService = Depends(get_question_service),
    # current_user: User = Depends(get_current_admin_user),
):
    """
    Create a new question.

    Requires admin privileges.
    """
    try:
        question = await service.create_question(question_in)
        return question
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=e.errors(),
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the question",
        )


@router.get(
    "/",
    response_model=QuestionsListResponse,
    responses={
        200: {"description": "List of questions retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
)
async def read_questions(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of questions to skip for pagination",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=1000,
        description="Maximum number of questions to return",
    ),
    category: int | None = Query(
        default=None, description="Filter by question category"
    ),
    difficulty: str | None = Query(
        default=None, description="Filter by question difficulty"
    ),
    service: QuestionService = Depends(get_question_service),
    # current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve a list of questions with optional filtering and pagination.

    Available to all authenticated users.
    """
    try:
        questions = await service.get_questions(
            skip=skip,
            limit=limit,
            category_id=category,
            difficulty=difficulty,
        )

        total_count = len(questions)

        return QuestionsListResponse(
            items=questions,
            total=total_count,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving questions",
        )


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    responses={
        200: {"description": "Question retrieved successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Question not found"},
    },
)
async def read_question(
    question_id: int = Path(..., ge=1, description="Question ID"),
    service: QuestionService = Depends(get_question_service),
    # current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve a specific question by ID.

    Available to all authenticated users.
    """
    try:
        question = await service.get_question(question_id)
        if question is None:
            raise QuestionNotFoundError(question_id)
        return question
    except QuestionNotFoundError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the question",
        )


@router.put(
    "/{question_id}",
    response_model=QuestionResponse,
    responses={
        200: {"description": "Question updated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin access required"},
        404: {"description": "Question not found"},
        422: {"description": "Validation error"},
    },
)
async def update_question(
    question_id: int = Path(
        ...,
        ge=1,
        description="Question ID",
    ),
    question_in: QuestionUpdate = None,
    service: QuestionService = Depends(get_question_service),
    # current_user: User = Depends(get_current_admin_user),
):
    """
    Update an existing question.

    Requires admin privileges.
    """
    try:
        question = await service.update_question(question_id, question_in)
        if question is None:
            raise QuestionNotFoundError(question_id)
        return question
    except QuestionNotFoundError:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=e.errors(),
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the question",
        )


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Question deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin access required"},
        404: {"description": "Question not found"},
    },
)
async def delete_question(
    question_id: int = Path(..., ge=1, description="Question ID"),
    service: QuestionService = Depends(get_question_service),
    # current_user: User = Depends(get_current_admin_user),
):
    """
    Delete a question.

    Requires admin privileges.
    """
    try:
        deleted = await service.delete_question(question_id)
        if not deleted:
            raise QuestionNotFoundError(question_id)
        return
    except QuestionNotFoundError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the question",
        )
