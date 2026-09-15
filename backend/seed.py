from datetime import date

from database import SessionLocal, Base, engine
from database_models import User, Chat, Message, Document, KnowledgeBase
from auth_logic import get_password_hash


# -------------------------
# Reset database tables
# -------------------------

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


db = SessionLocal()


try:
    # -------------------------
    # Users
    # -------------------------

    user1 = User(
        name="Fatimah",
        username="fatimah",
        password=get_password_hash("password")
    )

    user2 = User(
        name="Ahmed",
        username="ahmed",
        password=get_password_hash("password")
    )

    db.add_all([user1, user2])
    db.flush()


    # -------------------------
    # Chats
    # -------------------------

    chat1 = Chat(
        title="Docker Questions",
        created_date=date(2026, 9, 10),
        update_date=date(2026, 9, 10),
        user_id=user1.id
    )

    chat2 = Chat(
        title="Terraform Help",
        created_date=date(2026, 9, 11),
        update_date=date(2026, 9, 14),
        user_id=user1.id
    )

    chat3 = Chat(
        title="FastAPI Project",
        created_date=date(2026, 9, 12),
        update_date=date(2026, 9, 12),
        user_id=user2.id
    )

    db.add_all([chat1, chat2, chat3])
    db.flush()


    # -------------------------
    # Messages
    # -------------------------

    messages = [
        Message(
            role="user",
            content="What is Docker?",
            created_date=date(2026, 9, 10),
            chat_id=chat1.id
        ),

        Message(
            role="assistant",
            content="Docker is a platform for running applications inside containers.",
            created_date=date(2026, 9, 10),
            chat_id=chat1.id
        ),

        Message(
            role="user",
            content="What is Terraform?",
            created_date=date(2026, 9, 11),
            chat_id=chat2.id
        ),

        Message(
            role="assistant",
            content="Terraform is an infrastructure as code tool.",
            created_date=date(2026, 9, 11),
            chat_id=chat2.id
        ),

        Message(
            role="user",
            content="How do I create a FastAPI route?",
            created_date=date(2026, 9, 12),
            chat_id=chat3.id
        ),

        Message(
            role="assistant",
            content="You can create a route using FastAPI decorators such as @app.get().",
            created_date=date(2026, 9, 12),
            chat_id=chat3.id
        )
    ]

    db.add_all(messages)


    # -------------------------
    # Knowledge Bases
    # -------------------------

    knowledge1 = KnowledgeBase(
        title="Company Policies",
        description="Internal company policies and procedures.",
        created_date=date(2026, 9, 1),
        updated_date=date(2026, 9, 10),
        user_id=user1.id
    )

    knowledge2 = KnowledgeBase(
        title="Technical Documentation",
        description="Technical documentation for internal projects.",
        created_date=date(2026, 9, 5),
        updated_date=date(2026, 9, 14),
        user_id=user2.id
    )

    db.add_all([knowledge1, knowledge2])
    db.flush()


    # -------------------------
    # Documents
    # -------------------------

    document1 = Document(
        name="company-policy.pdf",
        created_date=date(2026, 9, 2),
        chat_id=None,
        knowledge_id=knowledge1.id
    )

    document2 = Document(
        name="security-policy.pdf",
        created_date=date(2026, 9, 3),
        chat_id=None,
        knowledge_id=knowledge1.id
    )

    document3 = Document(
        name="terraform-guide.pdf",
        created_date=date(2026, 9, 6),
        chat_id=chat2.id,
        knowledge_id=knowledge2.id
    )

    document4 = Document(
        name="docker-notes.pdf",
        created_date=date(2026, 9, 10),
        chat_id=chat1.id,
        knowledge_id=None
    )

    db.add_all([
        document1,
        document2,
        document3,
        document4
    ])


    # -------------------------
    # Save everything
    # -------------------------

    db.commit()

    print("Database reset and seeded successfully!")


except Exception:
    db.rollback()
    raise

finally:
    db.close()