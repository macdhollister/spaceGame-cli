from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"] if "DATABASE_URL" in os.environ else "sqlite://"
DEBUG = True if "DEBUG" in os.environ else False

if DEBUG:
    print("Database name: " + SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
