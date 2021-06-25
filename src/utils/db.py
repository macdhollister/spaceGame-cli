from uuid import uuid4

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src import models


def generate_id():
    return str(uuid4())[:7]


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


class Database:
    def __init__(self, db_url="sqlite://"):
        self.db_url = db_url

    def make_engine(self):
        engine = create_engine(self.db_url, connect_args={"check_same_thread": False})
        event.listen(engine, 'connect', _fk_pragma_on_connect)
        return engine

    def get_db(self):
        engine = self.make_engine()
        models.Base.metadata.create_all(bind=engine)
        session_local = sessionmaker()
        db = session_local(autocommit=False, autoflush=False, bind=engine)
        return db
