import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event

from src import models

Session = sessionmaker()


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


@pytest.fixture(scope='module')
def connection():
    engine = create_engine('sqlite://')
    event.listen(engine, 'connect', _fk_pragma_on_connect)

    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope='function')
def session(connection):
    models.Base.metadata.create_all(bind=connection)

    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
