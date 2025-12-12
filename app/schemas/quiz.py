from typing import List, Optional

from pydantic import BaseModel

from app.models.quiz import DifficultyLevel


class QuizRequest(BaseModel):
    difficulty: Optional[DifficultyLevel] = None
    num_questions: int = 10


class UserAnswer(BaseModel):
    question_id: int
    answer_id: int


class QuizSubmit(BaseModel):
    answers: List[UserAnswer]


class QuizResult(BaseModel):
    question_id: int
    user_answer_id: int
    correct_answer_id: int
    is_correct: bool
    explanation: Optional[str]


class QuizResponse(BaseModel):
    score: int
    total_questions: int
    percentage: float
    results: List[QuizResult]


class LeaderboardEntry(BaseModel):
    username: str
    total_score: int
    games_played: int
    avg_score: float


class UserStats(BaseModel):
    total_score: int
    games_played: int
    correct_answers: int
    total_answers: int
    accuracy: float
    by_category: dict
    by_difficulty: dict
