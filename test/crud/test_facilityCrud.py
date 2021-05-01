from src.crud import planetCrud, facilityCrud
from src.utils.colonyUtils import ColonyType
from src.utils.facilityUtils import FacilityLevel, FacilityType

from src.utils.planetUtils import SpecialPlanet
from test.conftest import *


def test_query_facility_by_id(session):
    FacilityFactory(id="abc")
    assert facilityCrud.query_facility_by_id(session, "abc").one()


def test_get_facilities(session):
    FacilityFactory(id="a")
    FacilityFactory(id="b")
    FacilityFactory(id="c")

    facilities = facilityCrud.get_facilities(session)

    assert len(facilities) == 3


def test_query_facilities_on_planet(session):
    FacilityFactory(planet="planet_a")
    FacilityFactory(planet="planet_a")
    FacilityFactory(planet="planet_b")
    FacilityFactory(planet="planet_b")
    FacilityFactory(planet="planet_b")

    planet_a_facilities = facilityCrud.query_facilities_on_planet(session, "planet_a").all()
    planet_b_facilities = facilityCrud.query_facilities_on_planet(session, "planet_b").all()

    assert len(planet_a_facilities) == 2
    assert len(planet_b_facilities) == 3


def test_create_facility_from_dict__proper_conditions(session):
    PlanetFactory(name="planet_a", owner="faction_1")
    facility_fixture = {
        'planet': 'planet_a',
        'facility_type': 'factory'
    }

    facilities = facilityCrud.get_facilities(session)
    assert len(facilities) == 0

    facilityCrud.create_facility_from_dict(session, facility_fixture)

    facilities = facilityCrud.get_facilities(session)
    assert len(facilities) == 1


def test_create_facility_from_dict__unowned_planet(session):
    PlanetFactory(name="planet_a")
    facility_fixture = {
        'planet': 'planet_a',
        'facility_type': 'factory'
    }

    facilities = facilityCrud.get_facilities(session)
    assert len(facilities) == 0

    with pytest.raises(ValueError) as error_info:
        facilityCrud.create_facility_from_dict(session, facility_fixture)

    facilities = facilityCrud.get_facilities(session)

    assert str(error_info.value) == "Cannot create facility on un-claimed planet."
    assert len(facilities) == 0


def test_create_facility_from_dict__improper_facility(session):
    PlanetFactory(name="planet_a", owner="faction_1")
    facility_fixture = {
        'planet': 'planet_a',
        'facility_type': 'not_a_proper_facility'
    }

    facilities = facilityCrud.get_facilities(session)
    assert len(facilities) == 0

    with pytest.raises(ValueError) as error_info:
        facilityCrud.create_facility_from_dict(session, facility_fixture)

    assert str(error_info.value) == "not_a_proper_facility is not a valid FacilityType"


def test_create_facility_from_dict__improper_planet(session):
    PlanetFactory(name="planet_a", owner="faction_1")
    facility_fixture = {
        'planet': 'not_a_planet',
        'facility_type': 'factory'
    }

    facilities = facilityCrud.get_facilities(session)
    assert len(facilities) == 0

    with pytest.raises(ValueError) as error_info:
        facilityCrud.create_facility_from_dict(session, facility_fixture)

    assert str(error_info.value) == "Planet 'not_a_planet' does not exist"

