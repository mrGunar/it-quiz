import asyncio
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from faker import Faker

from app.models.quiz import DifficultyLevel
from app.models.questions import Question
from app.models.answers import Answer

from app.models.user import User
from app.core.security import get_password_hash

fake = Faker()

IT_QUESTIONS = [
    {
        "category": "Python",
        "difficulty": DifficultyLevel.EASY,
        "question": "What is the output of 'print(2 ** 3)' in Python?",
        "answers": [
            {"text": "6", "is_correct": False},
            {"text": "8", "is_correct": True},
            {"text": "9", "is_correct": False},
            {"text": "5", "is_correct": False},
        ],
        "explanation": "** is the exponentiation operator in Python.",
    },
    {
        "category": "Python",
        "difficulty": DifficultyLevel.MEDIUM,
        "question": "Which of these is NOT a Python built-in data structure?",
        "answers": [
            {"text": "List", "is_correct": False},
            {"text": "Tuple", "is_correct": False},
            {"text": "HashMap", "is_correct": True},
            {"text": "Set", "is_correct": False},
        ],
        "explanation": "HashMap is not a built-in data structure; Python has dict instead.",
    },
    {
        "category": "JAVASCRIPT",
        "difficulty": DifficultyLevel.EASY,
        "question": "Which keyword is used to declare a variable in JavaScript?",
        "answers": [
            {"text": "var", "is_correct": False},
            {"text": "let", "is_correct": False},
            {"text": "const", "is_correct": False},
            {"text": "All of the above", "is_correct": True},
        ],
        "explanation": "JavaScript supports var, let, and const for variable declaration.",
    },
    {
        "category": "DATABASE",
        "difficulty": DifficultyLevel.MEDIUM,
        "question": "What does ACID stand for in database transactions?",
        "answers": [
            {
                "text": "Atomicity, Consistency, Isolation, Durability",
                "is_correct": True,
            },
            {
                "text": "Availability, Consistency, Integrity, Durability",
                "is_correct": False,
            },
            {
                "text": "Atomicity, Concurrency, Isolation, Durability",
                "is_correct": False,
            },
            {"text": "All of the above", "is_correct": False},
        ],
        "explanation": "ACID properties ensure reliable processing of database transactions.",
    },
    {
        "category": "DEVOPS",
        "difficulty": DifficultyLevel.HARD,
        "question": "What is the purpose of a Kubernetes Ingress?",
        "answers": [
            {
                "text": "To manage external access to services in a cluster",
                "is_correct": True,
            },
            {"text": "To store configuration data", "is_correct": False},
            {"text": "To manage internal service discovery", "is_correct": False},
            {"text": "To schedule pods on nodes", "is_correct": False},
        ],
        "explanation": "Ingress manages external HTTP/HTTPS access to services in a Kubernetes cluster.",
    },
    {
        "category": "ALGORITHMS",
        "difficulty": DifficultyLevel.MEDIUM,
        "question": "What is the time complexity of binary search?",
        "answers": [
            {"text": "O(n)", "is_correct": False},
            {"text": "O(log n)", "is_correct": True},
            {"text": "O(n log n)", "is_correct": False},
            {"text": "O(1)", "is_correct": False},
        ],
        "explanation": "Binary search halves the search space with each comparison.",
    },
    {
        "category": "SECURITY",
        "difficulty": DifficultyLevel.MEDIUM,
        "question": "What is the purpose of CSRF tokens?",
        "answers": [
            {"text": "To encrypt user passwords", "is_correct": False},
            {
                "text": "To prevent cross-site request forgery attacks",
                "is_correct": True,
            },
            {"text": "To validate user sessions", "is_correct": False},
            {"text": "To prevent SQL injection", "is_correct": False},
        ],
        "explanation": "CSRF tokens ensure that requests originate from trusted sources.",
    },
    {
        "category": "ML_AI",
        "difficulty": DifficultyLevel.HARD,
        "question": "What is the purpose of dropout in neural networks?",
        "answers": [
            {"text": "To increase training speed", "is_correct": False},
            {"text": "To prevent overfitting", "is_correct": True},
            {"text": "To reduce memory usage", "is_correct": False},
            {"text": "To improve accuracy", "is_correct": False},
        ],
        "explanation": "Dropout randomly ignores neurons during training to prevent overfitting.",
    },
]


async def seed_database(db: AsyncSession):
    """Seed the database with initial data"""

    admin_user = await db.execute(text("SELECT * FROM users WHERE username = 'admin'"))
    if not admin_user.first():
        admin = User(
            username="admin",
            email="admin@quiz.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
        )
        db.add(admin)

    for i in range(5):
        username = f"user{i+1}"
        user = await db.execute(
            text(f"SELECT * FROM users WHERE username = '{username}'")
        )
        if not user.first():
            new_user = User(
                username=username,
                email=f"user{i+1}@quiz.com",
                hashed_password=get_password_hash("password123"),
                total_score=random.randint(0, 1000),
                games_played=random.randint(1, 20),
            )
            db.add(new_user)

    await db.commit()

    existing_questions = await db.execute(text("SELECT COUNT(*) FROM questions"))
    count = existing_questions.scalar()

    if count == 0:
        for q_data in IT_QUESTIONS:
            question = Question(
                question_text=q_data["question"],
                category=q_data["category"],
                difficulty=q_data["difficulty"],
                explanation=q_data["explanation"],
            )

            for a_data in q_data["answers"]:
                answer = Answer(
                    answer_text=a_data["text"], is_correct=a_data["is_correct"]
                )
                question.answers.append(answer)

            db.add(question)

        await db.commit()
        print("Database seeded successfully!")
    else:
        print(f"Database already has {count} questions. Skipping seeding.")


async def main():
    """Main function to run seeding"""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        await seed_database(db)


if __name__ == "__main__":
    asyncio.run(main())
