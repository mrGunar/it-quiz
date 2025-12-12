from typing import List, Optional
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from app.models.quiz import DifficultyLevel
from app.models.questions import Question
from app.models.answers import Answer
from app.models.user_responses import UserResponse
from app.models.categories import Category
from app.schemas.quiz import QuizRequest
from app.schemas.questions import QuestionCreate
from app.models.user import User


class CRUDQuiz:
    @staticmethod
    async def create_question(
        db: AsyncSession, question_in: QuestionCreate
    ) -> Question:
        db_question = Question(
            question_text=question_in.question_text,
            category=question_in.category,
            difficulty=question_in.difficulty,
            explanation=question_in.explanation,
        )

        for answer_in in question_in.answers:
            db_answer = Answer(
                answer_text=answer_in.answer_text, is_correct=answer_in.is_correct
            )
            db_question.answers.append(db_answer)

        db.add(db_question)
        await db.commit()
        await db.refresh(db_question)
        return db_question

    @staticmethod
    async def get_question(db: AsyncSession, question_id: int) -> Optional[Question]:
        result = await db.execute(select(Question).filter(Question.id == question_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_questions(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category: Optional[Category] = None,
        difficulty: Optional[DifficultyLevel] = None,
    ) -> List[Question]:
        query = select(Question)

        if category:
            query = query.filter(Question.category == category)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def generate_quiz(
        db: AsyncSession, quiz_request: QuizRequest
    ) -> List[Question]:
        query = select(Question)

        if quiz_request.category:
            query = query.filter(Question.category == quiz_request.category)
        if quiz_request.difficulty:
            query = query.filter(Question.difficulty == quiz_request.difficulty)

        result = await db.execute(query)
        all_questions = result.scalars().all()

        selected_questions = random.sample(
            all_questions, min(quiz_request.num_questions, len(all_questions))
        )

        for question in selected_questions:
            random.shuffle(question.answers)

        return selected_questions

    @staticmethod
    async def submit_quiz(db: AsyncSession, user_id: int, answers: List[dict]) -> dict:
        score = 0
        results = []

        for user_answer in answers:
            result = await db.execute(
                select(Question, Answer)
                .join(Answer, Question.id == Answer.question_id)
                .filter(
                    and_(
                        Question.id == user_answer["question_id"],
                        Answer.is_correct == True,
                    )
                )
            )
            question_row = result.first()

            if question_row:
                question, correct_answer = question_row
                is_correct = user_answer["answer_id"] == correct_answer.id

                if is_correct:
                    score += 1

                db_response = UserResponse(
                    user_id=user_id,
                    question_id=user_answer["question_id"],
                    answer_id=user_answer["answer_id"],
                    is_correct=is_correct,
                )
                db.add(db_response)

                results.append(
                    {
                        "question_id": user_answer["question_id"],
                        "user_answer_id": user_answer["answer_id"],
                        "correct_answer_id": correct_answer.id,
                        "is_correct": is_correct,
                        "explanation": question.explanation,
                    }
                )

        await db.commit()

        return {
            "score": score,
            "total_questions": len(answers),
            "percentage": (score / len(answers)) * 100 if answers else 0,
            "results": results,
        }

    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: int) -> dict:
        result = await db.execute(
            select(func.count(UserResponse.id)).filter(UserResponse.user_id == user_id)
        )
        total_answers = result.scalar() or 0

        result = await db.execute(
            select(func.count(UserResponse.id)).filter(
                and_(UserResponse.user_id == user_id, UserResponse.is_correct == True)
            )
        )
        correct_answers = result.scalar() or 0

        result = await db.execute(
            select(
                Question.category,
                func.count(UserResponse.id).label("total"),
                func.sum(func.cast(UserResponse.is_correct, Integer)).label("correct"),
            )
            .join(Question, UserResponse.question_id == Question.id)
            .filter(UserResponse.user_id == user_id)
            .group_by(Question.category)
        )
        by_category = {}
        for row in result:
            by_category[row.category.value] = {
                "total": row.total,
                "correct": row.correct or 0,
                "accuracy": (
                    (row.correct or 0) / row.total * 100 if row.total > 0 else 0
                ),
            }

        result = await db.execute(
            select(
                Question.difficulty,
                func.count(UserResponse.id).label("total"),
                func.sum(func.cast(UserResponse.is_correct, Integer)).label("correct"),
            )
            .join(Question, UserResponse.question_id == Question.id)
            .filter(UserResponse.user_id == user_id)
            .group_by(Question.difficulty)
        )
        by_difficulty = {}
        for row in result:
            by_difficulty[row.difficulty.value] = {
                "total": row.total,
                "correct": row.correct or 0,
                "accuracy": (
                    (row.correct or 0) / row.total * 100 if row.total > 0 else 0
                ),
            }

        return {
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "accuracy": (
                (correct_answers / total_answers * 100) if total_answers > 0 else 0
            ),
            "by_category": by_category,
            "by_difficulty": by_difficulty,
        }


crud_quiz = CRUDQuiz()
