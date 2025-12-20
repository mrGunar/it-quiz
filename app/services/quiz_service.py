from typing import Any

from app.repositories import RepositoryFactory
from app.schemas.quiz import QuizRequest, QuizSubmit


class QuizService:
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory

    async def generate_quiz(self, quiz_request: QuizRequest) -> list[dict[str, Any]]:
        """Generate a simple quiz game."""

        difficult = quiz_request.difficulty.upper() if quiz_request.difficulty else None
        questions = await self.repo_factory.questions.get_random_questions(
            category_id=quiz_request.category_id,
            difficulty=difficult,
            limit=quiz_request.num_questions,
        )

        formatted_questions = []
        for question in questions:
            formatted_questions.append(
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "category": await self.repo_factory.categories.get(
                        question.category_id
                    ),
                    "explanation": question.explanation,
                    "difficulty": question.difficulty.value,
                    "answers": [
                        {"id": answer.id, "answer_text": answer.answer_text}
                        for answer in await self.repo_factory.answers.get_by_question_id(
                            question.id
                        )
                    ],
                }
            )

        return formatted_questions

    async def submit_quiz(
        self, user_id: int, quiz_submit: QuizSubmit
    ) -> dict[str, Any]:
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
