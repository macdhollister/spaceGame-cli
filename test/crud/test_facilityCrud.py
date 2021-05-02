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


def test_upgrade_facility(session):
    FacilityFactory(id="1", level=FacilityLevel.BASIC)
    FacilityFactory(id="2", level=FacilityLevel.INTERMEDIATE)
    FacilityFactory(id="3", level=FacilityLevel.ADVANCED)

    facilityCrud.upgrade_facility(session, "1")
    facilityCrud.upgrade_facility(session, "2")
    with pytest.raises(ValueError) as error_info:
        facilityCrud.upgrade_facility(session, "3")

    facility_1 = facilityCrud.query_facility_by_id(session, "1").first()
    facility_2 = facilityCrud.query_facility_by_id(session, "2").first()
    facility_3 = facilityCrud.query_facility_by_id(session, "3").first()

    assert facility_1.level == FacilityLevel.INTERMEDIATE
    assert facility_2.level == FacilityLevel.ADVANCED
    assert facility_3.level == FacilityLevel.ADVANCED
    assert str(error_info.value) == "Only basic and intermediate facilities can be upgraded."


def test_downgrade_facility(session):
    FacilityFactory(id="1", level=FacilityLevel.BASIC)
    FacilityFactory(id="2", level=FacilityLevel.INTERMEDIATE)
    FacilityFactory(id="3", level=FacilityLevel.ADVANCED)

    facilityCrud.downgrade_facility(session, "1")
    facilityCrud.downgrade_facility(session, "2")
    facilityCrud.downgrade_facility(session, "3")

    facility_1 = facilityCrud.query_facility_by_id(session, "1").first()
    facility_2 = facilityCrud.query_facility_by_id(session, "2").first()
    facility_3 = facilityCrud.query_facility_by_id(session, "3").first()

    assert facility_1 is None
    assert facility_2.level == FacilityLevel.BASIC
    assert facility_3.level == FacilityLevel.INTERMEDIATE


def test_damage_facility(session):
    FacilityFactory(id="a", shields=0)
    FacilityFactory(id="b", shields=1)
    FacilityFactory(id="c", shields=2)
    FacilityFactory(id="d", level=FacilityLevel.INTERMEDIATE, shields=0)

    facilityCrud.damage_facility(session, "a")
    facilityCrud.damage_facility(session, "b")
    facilityCrud.damage_facility(session, "c")
    facilityCrud.damage_facility(session, "d")

    planet_a = facilityCrud.query_facility_by_id(session, "a").first()
    planet_b = facilityCrud.query_facility_by_id(session, "b").first()
    planet_c = facilityCrud.query_facility_by_id(session, "c").first()
    planet_d = facilityCrud.query_facility_by_id(session, "d").first()

    assert planet_a is None
    assert planet_b.shields == 0
    assert planet_c.shields == 1
    assert planet_d.shields == 0
    assert planet_d.level == FacilityLevel.BASIC


def test_destroy_facility(session):
    FacilityFactory(id="a")
    FacilityFactory(id="b")
    FacilityFactory(id="c")

    facilityCrud.destroy_facility(session, "a")
    facilityCrud.destroy_facility(session, "c")

    all_facilities = facilityCrud.get_facilities(session)

    assert len(all_facilities) == 1
    assert all_facilities[0].id == "b"


def test_get_shield_contribution(session):
    fac_a = FacilityFactory(id="a", facility_type=FacilityType.FACTORY)
    fac_b = FacilityFactory(id="b", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.BASIC)
    fac_c = FacilityFactory(id="c", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.INTERMEDIATE)
    fac_d = FacilityFactory(id="d", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.ADVANCED)

    assert facilityCrud.get_shield_contribution(fac_a) == 0
    assert facilityCrud.get_shield_contribution(fac_b) == 1
    assert facilityCrud.get_shield_contribution(fac_c) == 2
    assert facilityCrud.get_shield_contribution(fac_d) == 3


def test_get_planet_shield_points(session):
    # Planet without shields
    PlanetFactory(name="planet_a")

    # Planet with single basic shield
    PlanetFactory(name="planet_b")
    FacilityFactory(planet="planet_b", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.BASIC)

    # Planet with multiple shields of varying types
    PlanetFactory(name="planet_c")
    FacilityFactory(planet="planet_c", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.BASIC)
    FacilityFactory(planet="planet_c", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.INTERMEDIATE)
    FacilityFactory(planet="planet_c", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.ADVANCED)

    assert facilityCrud.get_planet_shield_points(session, "planet_a") == 0
    assert facilityCrud.get_planet_shield_points(session, "planet_b") == 1
    assert facilityCrud.get_planet_shield_points(session, "planet_c") == 6


def test_restore_planet_facilities(session):
    # Planet without shields
    PlanetFactory(name="planet_a")
    FacilityFactory(id="a1", planet="planet_a")
    FacilityFactory(id="a2", planet="planet_a")

    # Planet with single basic shield
    PlanetFactory(name="planet_b")
    FacilityFactory(id="b1", planet="planet_b", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.BASIC)
    FacilityFactory(id="b2", planet="planet_b")

    # Planet with multiple shields of varying types
    PlanetFactory(name="planet_c")
    FacilityFactory(id="c1", planet="planet_c", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.BASIC)
    FacilityFactory(id="c2", planet="planet_c", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.INTERMEDIATE)
    FacilityFactory(id="c3", planet="planet_c", facility_type=FacilityType.PLANETARY_SHIELDS, level=FacilityLevel.ADVANCED)
    FacilityFactory(id="c4", planet="planet_c")

    facilityCrud.restore_planet_facilities(session, "planet_a")
    facilityCrud.restore_planet_facilities(session, "planet_b")
    facilityCrud.restore_planet_facilities(session, "planet_c")

    assert facilityCrud.query_facility_by_id(session, "a1").first().shields == 0
    assert facilityCrud.query_facility_by_id(session, "a2").first().shields == 0

    assert facilityCrud.query_facility_by_id(session, "b1").first().shields == 1
    assert facilityCrud.query_facility_by_id(session, "b2").first().shields == 1

    assert facilityCrud.query_facility_by_id(session, "c1").first().shields == 6
    assert facilityCrud.query_facility_by_id(session, "c2").first().shields == 6
    assert facilityCrud.query_facility_by_id(session, "c3").first().shields == 6
    assert facilityCrud.query_facility_by_id(session, "c4").first().shields == 6
