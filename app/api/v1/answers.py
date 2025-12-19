from fastapi import APIRouter, Depends, HTTPException

from app.services.answer_service import AnswerService
from app.api.dependencies import get_answer_service
from app.schemas.answers import AnswerCreate, AnswerResponse, AnswerUpdate
from app.middleware.logger import logger

router = APIRouter()


@router.get("/", response_model=list[AnswerResponse])
async def get_answers_for_question_by_id(
    question_id: int,
    service: AnswerService = Depends(get_answer_service),
):
    answers = await service.get_for_question_by_id(question_id)

    if not answers:
        raise HTTPException(
            status_code=404, detail="There are no answers for this question."
        )
    return answers


@router.post(
    "/",
    response_model=AnswerResponse,
    status_code=201,
)
async def create(
    answer_in: AnswerCreate,
    service: AnswerService = Depends(get_answer_service),
):
    """Create an answer."""
    try:
        answer = await service.create_for_question(answer_in)
        return answer
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.put("/{answer_id}", response_model=AnswerResponse)
async def update(
    answer_id: int,
    answer_in: AnswerUpdate,
    service: AnswerService = Depends(get_answer_service),
):
    """Update the answer by id."""
    try:
        answer = await service.update(answer_id, answer_in)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

    logger.info("An answer has been updated successfully.")
    if answer is None:
        logger.error(f"Failed to update an answer. The answer not found.")
        raise HTTPException(status_code=400, detail="The answer not found")
    return answer


@router.delete(
    "/{answer_id}",
    status_code=204,
)
async def delete(
    answer_id: int,
    service: AnswerService = Depends(get_answer_service),
):
    """Delete an answer by id."""
    deleted = await service.delete(answer_id)
    logger.info("The answer has been deleted successfully.")
    if not deleted:
        logger.error(
            f"Failed to delete a answer by id: `{answer_id}`. The answer not found."
        )
        raise HTTPException(status_code=404, detail="The answer not found")
    return {"message": "Answer deleted successfully"}
