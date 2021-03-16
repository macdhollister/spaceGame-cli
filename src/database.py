from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


load_dotenv()
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"] if "DATABASE_URL" in os.environ else "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

event.listen(engine, 'connect', _fk_pragma_on_connect)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
