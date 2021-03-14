from src import models
from src.database import SessionLocal, engine


def get_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    return db
