import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from dotenv import load_dotenv
load_dotenv()

from app.database.postgres import Base, engine
from app.models.conversation import Conversation, Message


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Conversation tables created successfully!")


if __name__ == "__main__":
    create_tables()