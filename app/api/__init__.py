from fastapi import APIRouter
from app.api.v1 import difficulties, user, quiz, categories, questions

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(
    difficulties.router, prefix="/difficilties", tags=["difficilties"]
)
