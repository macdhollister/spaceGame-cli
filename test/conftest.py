import factory
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import models
from src.models import Facility, Faction, Ship, Planet

Session = sessionmaker()


class FacilityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Facility


class FactionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Faction


class PlanetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Planet


class ShipFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Ship

    # Defaults
    modules = "D1"


@pytest.fixture(scope='module')
def connection():
    engine = create_engine('sqlite://')

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


@pytest.fixture(scope='function', autouse=True)
def set_factory_session(session):
    FacilityFactory._meta.sqlalchemy_session = session
    FactionFactory._meta.sqlalchemy_session = session
    PlanetFactory._meta.sqlalchemy_session = session
    ShipFactory._meta.sqlalchemy_session = session
