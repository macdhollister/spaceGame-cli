from src import models
from src.database import SessionLocal, engine
from uuid import uuid4


def get_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    return db


def generate_id():
    return str(uuid4())[:7]
