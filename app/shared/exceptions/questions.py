from fastapi import HTTPException
from fastapi import status


class QuestionNotFoundError(HTTPException):
    def __init__(self, question_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found",
        )


class QuestionCreationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Failed to create question: {detail}",
        )
