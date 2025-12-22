from typing import List, Dict, Any, Optional

from app.repositories import RepositoryFactory
from app.schemas.quiz import QuizRequest, QuizSubmit
from app.schemas.questions import QuestionCreate, QuestionUpdate
from app.models.quiz import DifficultyLevel
from app.models.categories import Category


class QuestionService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def create_question(self, question_in: QuestionCreate):
        return await self.repo_factory.questions.create(question_in)

    async def get_question(self, question_id: int):
        return await self.repo_factory.questions.get_with_answers(question_id)

    async def get_questions(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[Category] = None,
        difficulty: Optional[DifficultyLevel] = None,
    ) -> List:
        filters = {}
        if category_id:
            filters["category_id"] = category_id
        if difficulty:
            filters["difficulty"] = difficulty

        return await self.repo_factory.questions.get_multi_with_answers(
            skip=skip, limit=limit, **filters
        )

    async def generate_quiz(self, quiz_request: QuizRequest) -> List[Dict[str, Any]]:
        questions = await self.repo_factory.questions.get_random_questions(
            category=quiz_request.category,
            difficulty=quiz_request.difficulty,
            limit=quiz_request.num_questions,
        )

        formatted_questions = []
        for question in questions:
            formatted_questions.append(
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "category": question.category.value,
                    "difficulty": question.difficulty.value,
                    "answers": [
                        {"id": answer.id, "answer_text": answer.answer_text}
                        for answer in question.answers
                    ],
                }
            )

        return formatted_questions

    async def submit_quiz(
        self, user_id: int, quiz_submit: QuizSubmit
    ) -> Dict[str, Any]:
        score = 0
        results = []

        for user_answer in quiz_submit.answers:
            correct_answer = await self.repo_factory.questions.get_correct_answer(
                user_answer.question_id
            )

            if not correct_answer:
                continue

            is_correct = user_answer.answer_id == correct_answer.id

            if is_correct:
                score += 1

            question = await self.repo_factory.questions.get(user_answer.question_id)

            await self.repo_factory.user_responses.create(
                user_id=user_id,
                question_id=user_answer.question_id,
                answer_id=user_answer.answer_id,
                is_correct=is_correct,
            )

            results.append(
                {
                    "question_id": user_answer.question_id,
                    "user_answer_id": user_answer.answer_id,
                    "correct_answer_id": correct_answer.id,
                    "is_correct": is_correct,
                    "explanation": question.explanation if question else None,
                }
            )

        await self.repo_factory.users.update_score(user_id, score)

        total_questions = len(quiz_submit.answers)

        return {
            "score": score,
            "total_questions": total_questions,
            "percentage": (score / total_questions * 100) if total_questions > 0 else 0,
            "results": results,
        }

    async def update_question(self, question_id: int, question_in: QuestionUpdate):
        return await self.repo_factory.questions.update(question_id, question_in)

    async def delete_question(self, question_id: int) -> bool:
        return await self.repo_factory.questions.delete(question_id)
