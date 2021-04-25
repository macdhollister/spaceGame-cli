from src import models
from src.database import engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4


def get_db(engine=engine):
    models.Base.metadata.create_all(bind=engine)
    session_local = sessionmaker()
    db = session_local(autocommit=False, autoflush=False, bind=engine)
    return db


def generate_id():
    return str(uuid4())[:7]
