from datetime import datetime
from io import BytesIO

from database import SessionLocal, Base, engine
from database_models import User, Chat, Message, Document, KnowledgeBase
from auth_logic import get_password_hash

from open_web_ui_api import (
    upload_file,
    wait_for_file_processing,
    create_knowledge,
    add_file_to_knowledge
)

# -------------------------
# Reset database tables
# -------------------------

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


db = SessionLocal()


# -------------------------
# Helper for seed files
# -------------------------

class SeedFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = BytesIO(content.encode("utf-8"))
        self.content_type = "text/plain"


# -------------------------
# Helper for Open WebUI IDs
# -------------------------

def get_open_webui_id(response):
    if "id" not in response:
        raise Exception(
            f"Open WebUI did not return an ID: {response}"
        )

    return response["id"]


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
        name="Reem",
        username="reem",
        password=get_password_hash("password")
    )

    user3 = User(
        name="Raghad",
        username="raghad",
        password=get_password_hash("password")
    )

    db.add_all([
        user1,
        user2,
        user3
    ])

    db.flush()


    # -------------------------
    # Chats
    # -------------------------

    chat1 = Chat(
        title="Docker Questions",
        created_date=datetime(2026, 9, 10),
        update_date=datetime(2026, 9, 10),
        user_id=user1.id
    )

    chat2 = Chat(
        title="Terraform Help",
        created_date=datetime(2026, 9, 11),
        update_date=datetime(2026, 9, 14),
        user_id=user1.id
    )

    chat3 = Chat(
        title="FastAPI Project",
        created_date=datetime(2026, 9, 12),
        update_date=datetime(2026, 9, 12),
        user_id=user2.id
    )

    chat4 = Chat(
        title="Company Policies",
        created_date=datetime(2026, 9, 13),
        update_date=datetime(2026, 9, 13),
        user_id=user3.id
    )

    db.add_all([
        chat1,
        chat2,
        chat3,
        chat4
    ])

    db.flush()

    messages = [

        # Fatimah - Docker
        Message(
            role="user",
            content="What is Docker?",
            created_date=datetime(2026, 9, 10),
            model_name=None,
            chat_id=chat1.id
        ),

        Message(
            role="assistant",
            content=(
                "Docker is a platform that packages applications "
                "and their dependencies into containers."
            ),
            created_date=datetime(2026, 9, 10),
            model_name="gemini-3.8-flash",
            chat_id=chat1.id
        ),


        # Fatimah - Terraform
        Message(
            role="user",
            content="What is Terraform?",
            created_date=datetime(2026, 9, 11),
            model_name=None,
            chat_id=chat2.id
        ),

        Message(
            role="assistant",
            content=(
                "Terraform is an infrastructure as code tool "
                "that allows you to define and manage infrastructure "
                "using configuration files."
            ),
            created_date=datetime(2026, 9, 11),
            model_name="gemini-3.8-flash",
            chat_id=chat2.id
        ),


        # Reem - FastAPI
        Message(
            role="user",
            content="How do I create a FastAPI route?",
            created_date=datetime(2026, 9, 12),
            model_name=None,
            chat_id=chat3.id
        ),

        Message(
            role="assistant",
            content=(
                "You can create a FastAPI route using decorators "
                "such as @app.get(), @app.post(), @app.put(), "
                "and @app.delete()."
            ),
            created_date=datetime(2026, 9, 12),
            model_name="gemini-3.8-flash",
            chat_id=chat3.id
        ),


        # Raghad - Company policies
        Message(
            role="user",
            content=(
                "What information is usually included "
                "in a company policy?"
            ),
            created_date=datetime(2026, 9, 13),
            model_name=None,
            chat_id=chat4.id
        ),

        Message(
            role="assistant",
            content=(
                "Company policies usually describe rules, "
                "procedures, responsibilities, and guidelines "
                "that employees are expected to follow."
            ),
            created_date=datetime(2026, 9, 13),
            model_name="gemini-3.8-flash",
            chat_id=chat4.id
        )
    ]

    db.add_all(messages)


    # -------------------------
    # Knowledge Base 1
    # -------------------------

    knowledge_response1 = create_knowledge(
        name="Company Policies",
        description="Internal company policies and procedures."
    )

    open_web_ui_knowledge_id1 = get_open_webui_id(
        knowledge_response1
    )

    knowledge1 = KnowledgeBase(
        title="Company Policies",
        description="Internal company policies and procedures.",
        created_date=datetime(2026, 9, 1),
        updated_date=datetime(2026, 9, 10),
        open_web_ui_knowledge_id=open_web_ui_knowledge_id1,
        user_id=user1.id
    )

    db.add(knowledge1)
    db.flush()


    # -------------------------
    # Knowledge Base 2
    # -------------------------

    knowledge_response2 = create_knowledge(
        name="Technical Documentation",
        description="Technical documentation for internal projects."
    )

    open_web_ui_knowledge_id2 = get_open_webui_id(
        knowledge_response2
    )

    knowledge2 = KnowledgeBase(
        title="Technical Documentation",
        description="Technical documentation for internal projects.",
        created_date=datetime(2026, 9, 5),
        updated_date=datetime(2026, 9, 14),
        open_web_ui_knowledge_id=open_web_ui_knowledge_id2,
        user_id=user2.id
    )

    db.add(knowledge2)
    db.flush()


    # -------------------------
    # Document 1
    # -------------------------

    company_policy = SeedFile(
        "company-policy.txt",
        """
Company Policy

Employees must follow the company's security,
privacy, and acceptable-use policies.

Company information must only be accessed
for authorized business purposes.
"""
    )

    file_response1 = upload_file(company_policy)

    open_web_ui_file_id1 = get_open_webui_id(
        file_response1
    )

    wait_for_file_processing(
        open_web_ui_file_id1
    )

    add_file_to_knowledge(
        open_web_ui_knowledge_id1,
        open_web_ui_file_id1
    )

    document1 = Document(
        name="company-policy.txt",
        created_date=datetime(2026, 9, 2),
        open_web_ui_file_id=open_web_ui_file_id1,
        chat_id=None,
        knowledge_id=knowledge1.id,
        user_id=user1.id
    )


    # -------------------------
    # Document 2
    # -------------------------

    security_policy = SeedFile(
        "security-policy.txt",
        """
Security Policy

Passwords must be kept private.

Employees must not share authentication credentials.

Sensitive company information should only be stored
in approved systems.
"""
    )

    file_response2 = upload_file(security_policy)

    open_web_ui_file_id2 = get_open_webui_id(
        file_response2
    )

    wait_for_file_processing(
        open_web_ui_file_id2
    )

    add_file_to_knowledge(
        open_web_ui_knowledge_id1,
        open_web_ui_file_id2
    )

    document2 = Document(
        name="security-policy.txt",
        created_date=datetime(2026, 9, 3),
        open_web_ui_file_id=open_web_ui_file_id2,
        chat_id=None,
        knowledge_id=knowledge1.id,
        user_id=user1.id
    )


    # -------------------------
    # Document 3
    # -------------------------

    terraform_guide = SeedFile(
        "terraform-guide.txt",
        """
Terraform Guide

Terraform is an infrastructure as code tool.

Terraform configuration files describe cloud resources.

Terraform can create, update, and delete
infrastructure based on the configuration.
"""
    )

    file_response3 = upload_file(terraform_guide)

    open_web_ui_file_id3 = get_open_webui_id(
        file_response3
    )

    wait_for_file_processing(
        open_web_ui_file_id3
    )

    add_file_to_knowledge(
        open_web_ui_knowledge_id2,
        open_web_ui_file_id3
    )

    document3 = Document(
        name="terraform-guide.txt",
        created_date=datetime(2026, 9, 6),
        open_web_ui_file_id=open_web_ui_file_id3,
        chat_id=chat3.id,
        knowledge_id=knowledge2.id,
        user_id=user2.id
    )


    # -------------------------
    # Document 4
    # -------------------------

    docker_notes = SeedFile(
        "docker-notes.txt",
        """
Docker Notes

Docker packages applications and their dependencies
into containers.

Docker Compose can be used to define and run
multiple containers together.
"""
    )

    file_response4 = upload_file(docker_notes)

    open_web_ui_file_id4 = get_open_webui_id(
        file_response4
    )

    wait_for_file_processing(
        open_web_ui_file_id4
    )

    document4 = Document(
        name="docker-notes.txt",
        created_date=datetime(2026, 9, 10),
        open_web_ui_file_id=open_web_ui_file_id4,
        chat_id=chat1.id,
        knowledge_id=None,
        user_id=user1.id
    )


    # -------------------------
    # Add documents to database
    # -------------------------

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

    print()
    print("Users:")
    print(f"Fatimah ID: {user1.id}")
    print(f"Reem ID: {user2.id}")
    print(f"Raghad ID: {user3.id}")

    print()
    print("Open WebUI knowledge IDs:")
    print(open_web_ui_knowledge_id1)
    print(open_web_ui_knowledge_id2)

    print()
    print("Open WebUI file IDs:")
    print(open_web_ui_file_id1)
    print(open_web_ui_file_id2)
    print(open_web_ui_file_id3)
    print(open_web_ui_file_id4)


except Exception:
    db.rollback()
    raise

finally:
    db.close()
