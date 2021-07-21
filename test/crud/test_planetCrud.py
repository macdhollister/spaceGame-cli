import pytest

from src.crud import planetCrud
from src.models import Planet
from src.utils.colonyUtils import ColonyType
from src.utils.facilityUtils import FacilityLevel, FacilityType
from src.utils.planetUtils import SpecialPlanet
from test.conftest import PlanetFactory, ShipFactory, FactionFactory, FacilityFactory


def test_build_map(session):
    map_fixture = [
        {
            "name": "planet_a",
            "size": "s",
            "resources": 4,
            "connections": ["planet_b", "planet_c"]
        },
        {
            "name": "planet_b",
            "size": "m",
            "resources": 3,
            "connections": ["planet_a", "planet_d"]
        },
        {
            "name": "planet_c",
            "size": "l",
            "resources": 2,
            "connections": ["planet_a", "planet_d"]
        },
        {
            "name": "planet_d",
            "size": "m",
            "resources": 4,
            "connections": ["planet_b", "planet_c"]
        }
    ]

    planetCrud.build_map(session, map_fixture)

    assert session.query(Planet).count() == 4

    stored_planets = session.query(Planet).all()
    assert sorted(map(lambda planet: planet.name, stored_planets)) == ['planet_a', 'planet_b', 'planet_c', 'planet_d']

    assert map_fixture == list(
        map(
            lambda planet: {
                'name': planet.name,
                'size': planet.size,
                'resources': planet.resources,
                'connections': sorted(list(map(lambda connection: connection.name, planet.connections)))
            },
            stored_planets
        )
    )


def test_get_planets(session):
    planet_a = PlanetFactory(name="planet_a", size="s", resources=4, special=SpecialPlanet.STANDARD)
    planet_b = PlanetFactory(name="planet_b", size="m", resources=3, special=SpecialPlanet.LOGISTICS)
    planet_a.connections = [planet_b]
    planet_b.connections = [planet_a]

    stored_planets = planetCrud.get_planets(session)
    assert planet_a in stored_planets
    assert planet_b in stored_planets
    assert len(stored_planets) == 2


def test_get_planet_names(session):
    PlanetFactory(name="planet_a")
    PlanetFactory(name="planet_b")

    stored_names = planetCrud.get_planet_names(session)

    assert "planet_a" in stored_names
    assert "planet_b" in stored_names
    assert len(stored_names) == 2


def test_get_planets_by_faction(session):
    faction_name = "faction_1"

    # Owned Planets
    PlanetFactory(name="planet_a", owner=faction_name)
    PlanetFactory(name="planet_b", owner=faction_name)

    # Observed Planets
    PlanetFactory(name="planet_c")
    ShipFactory(location="planet_c", owner=faction_name)

    # Other Planets
    PlanetFactory(name="planet_d")
    PlanetFactory(name="planet_e")

    owned_and_controlled = planetCrud.get_planets_by_faction(session, faction_name)

    controlled = owned_and_controlled['controlled']
    observed = owned_and_controlled['observed']

    assert len(controlled) == 2
    assert len(observed) == 1

    assert "planet_a" in list(map(lambda planet: planet.name, controlled))
    assert "planet_b" in list(map(lambda planet: planet.name, controlled))
    assert "planet_c" in list(map(lambda planet: planet.name, observed))


def test_get_planet_by_name(session):
    PlanetFactory(name="planet_a")
    PlanetFactory(name="planet_b")

    selected_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert selected_planet.name == "planet_a"


def test_claim_planet__unowned(session):
    PlanetFactory(name="planet_a")
    FactionFactory(faction_name="faction_1")

    planetCrud.claim_planet(session, "planet_a", "faction_1")
    claimed_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert claimed_planet.owner == "faction_1"


def test_claim_planet__owned(session):
    FactionFactory(faction_name="faction_1")
    FactionFactory(faction_name="faction_2")
    PlanetFactory(name="planet_a", owner="faction_2")

    unclaimed_planet = planetCrud.get_planet_by_name(session, "planet_a")
    assert unclaimed_planet.owner == "faction_2"

    planetCrud.claim_planet(session, "planet_a", "faction_1")
    claimed_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert claimed_planet.owner == "faction_1"


def test_reassign_planet__unowned(session):
    FactionFactory(faction_name="faction_1")
    PlanetFactory(name="planet_a")

    with pytest.raises(ValueError) as error_info:
        planetCrud.reassign_planet(session, "planet_a", "faction_1")

    assert str(error_info.value) == "planet_a not owned. Please use 'claim' or 'colonize'."


def test_reassign_planet__owned(session):
    FactionFactory(faction_name="faction_1")
    FactionFactory(faction_name="faction_2")
    PlanetFactory(name="planet_a", owner="faction_2")

    unclaimed_planet = planetCrud.get_planet_by_name(session, "planet_a")
    assert unclaimed_planet.owner == "faction_2"

    planetCrud.reassign_planet(session, "planet_a", "faction_1")
    claimed_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert claimed_planet.owner == "faction_1"


def test_colonize_planet__no_colony_ship(session):
    FactionFactory(faction_name="faction_1")
    PlanetFactory(name="planet_a")

    with pytest.raises(ValueError) as error_info:
        planetCrud.colonize_planet(session, "planet_a", "faction_1")

    stored_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert str(error_info.value) == "faction_1 does not have a colony ship on planet_a."
    assert stored_planet.owner is None


def test_colonize_planet__proper_conditions(session):
    FactionFactory(faction_name="faction_1")
    PlanetFactory(name="planet_a")
    ShipFactory(owner="faction_1", location="planet_a", modules="COLONY")

    planetCrud.colonize_planet(session, "planet_a", "faction_1")

    stored_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert stored_planet.owner == "faction_1"
    assert stored_planet.colony_size == ColonyType.COLONY
    assert stored_planet.ships == []


def test_colonize_planet__planet_owned_no_facilities(session):
    FactionFactory(faction_name="faction_1")
    FactionFactory(faction_name="faction_2")
    PlanetFactory(name="planet_a", owner="faction_2")
    ShipFactory(owner="faction_1", location="planet_a", modules="COLONY")

    planetCrud.colonize_planet(session, "planet_a", "faction_1")

    stored_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert stored_planet.owner == "faction_1"
    assert stored_planet.colony_size == ColonyType.COLONY
    assert stored_planet.ships == []


def test_colonize_planet__planet_owned_with_facilities(session):
    FactionFactory(faction_name="faction_1")
    FactionFactory(faction_name="faction_2")
    FacilityFactory(id="123", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY, planet="planet_a")
    PlanetFactory(name="planet_a", owner="faction_2")
    ShipFactory(owner="faction_1", location="planet_a", modules="COLONY")

    with pytest.raises(RuntimeError) as error_info:
        planetCrud.colonize_planet(session, "planet_a", "faction_1")

    stored_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert str(error_info.value) == "planet_a is owned by faction_2 and has facilities built. Cannot be colonized."
    assert stored_planet.owner == "faction_2"
    assert len(stored_planet.ships) == 1


def test_upgrade_colony_type__unowned(session):
    PlanetFactory(name="planet_a")

    with pytest.raises(ValueError) as error_info:
        planetCrud.upgrade_colony_type(session, "planet_a")

    assert str(error_info.value) == "planet_a is unowned. Cannot be upgraded."


def test_upgrade_colony_type__owned(session):
    PlanetFactory(name="planet_a", owner="faction_1", colony_size=ColonyType.COLONY)

    planetCrud.upgrade_colony_type(session, "planet_a")
    stored_planet = planetCrud.get_planet_by_name(session, "planet_a")

    assert stored_planet.colony_size == ColonyType.OUTPOST


def test_upgrade_colony_type__fortress(session):
    PlanetFactory(name="planet_a", owner="faction_1", colony_size=ColonyType.FORTRESS)

    with pytest.raises(ValueError) as error_info:
        planetCrud.upgrade_colony_type(session, "planet_a")

    assert str(error_info.value) == "Only colonies, outposts, and strongholds can be upgraded."


def test_planet_visible_by_faction__owned(session):
    PlanetFactory(name="planet_a", owner="faction_1")
    FactionFactory(faction_name="faction_1")

    assert planetCrud.planet_visible_by_faction(session, "planet_a", "faction_1")


def test_planet_visible_by_faction__unowned_with_ship(session):
    PlanetFactory(name="planet_a", owner="faction_2")
    FactionFactory(faction_name="faction_1")
    FactionFactory(faction_name="faction_2")
    ShipFactory(owner="faction_1", location="planet_a")

    assert planetCrud.planet_visible_by_faction(session, "planet_a", "faction_1")


def test_planet_visible_by_faction__unowned_without_ship(session):
    PlanetFactory(name="planet_a", owner="faction_2")
    FactionFactory(faction_name="faction_1")
    FactionFactory(faction_name="faction_2")

    assert not planetCrud.planet_visible_by_faction(session, "planet_a", "faction_1")


def test_get_connection_names(session):
    map_fixture = [
        {
            "name": "planet_a",
            "size": "s",
            "resources": 4,
            "connections": ["planet_b", "planet_c"]
        },
        {
            "name": "planet_b",
            "size": "m",
            "resources": 3,
            "connections": ["planet_a", "planet_d"]
        },
        {
            "name": "planet_c",
            "size": "l",
            "resources": 2,
            "connections": ["planet_a", "planet_d"]
        },
        {
            "name": "planet_d",
            "size": "m",
            "resources": 4,
            "connections": ["planet_b", "planet_c"]
        }
    ]

    planetCrud.build_map(session, map_fixture)

    assert sorted(planetCrud.get_connection_names(session, "planet_a")) == ["planet_b", "planet_c"]
    assert sorted(planetCrud.get_connection_names(session, "planet_b")) == ["planet_a", "planet_d"]
    assert sorted(planetCrud.get_connection_names(session, "planet_c")) == ["planet_a", "planet_d"]
    assert sorted(planetCrud.get_connection_names(session, "planet_d")) == ["planet_b", "planet_c"]


def test_get_lp_production(session):
    # No facilities
    PlanetFactory(name="planet_a")

    # Single basic HQ on standard world
    PlanetFactory(name="planet_b")
    FacilityFactory(planet="planet_b", level=FacilityLevel.BASIC, facility_type=FacilityType.FLEET_HQ)

    # Multiple HQs of various levels on standard world
    PlanetFactory(name="planet_c")
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FLEET_HQ)
    FacilityFactory(planet="planet_c", level=FacilityLevel.INTERMEDIATE, facility_type=FacilityType.FLEET_HQ)
    FacilityFactory(planet="planet_c", level=FacilityLevel.ADVANCED, facility_type=FacilityType.FLEET_HQ)

    # Multiple HQs of various levels on a Logistics Hub
    PlanetFactory(name="planet_d", special=SpecialPlanet.LOGISTICS)
    FacilityFactory(planet="planet_d", level=FacilityLevel.BASIC, facility_type=FacilityType.FLEET_HQ)
    FacilityFactory(planet="planet_d", level=FacilityLevel.ADVANCED, facility_type=FacilityType.FLEET_HQ)

    planet_a_lp = planetCrud.get_lp_production(session, "planet_a")
    planet_b_lp = planetCrud.get_lp_production(session, "planet_b")
    planet_c_lp = planetCrud.get_lp_production(session, "planet_c")
    planet_d_lp = planetCrud.get_lp_production(session, "planet_d")

    assert planet_a_lp == 0
    assert planet_b_lp == 2
    assert planet_c_lp == 14
    assert planet_d_lp == 12


def test_get_rp_production(session):
    # No facilities
    PlanetFactory(name="planet_a")

    # Single basic lab, standard world
    PlanetFactory(name="planet_b")
    FacilityFactory(planet="planet_b", level=FacilityLevel.BASIC, facility_type=FacilityType.LABORATORY)

    # Multiple labs of various levels on standard world
    PlanetFactory(name="planet_c")
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.LABORATORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.INTERMEDIATE, facility_type=FacilityType.LABORATORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.ADVANCED, facility_type=FacilityType.LABORATORY)

    # Multiple labs of various levels on an artifact world
    PlanetFactory(name="planet_d", special=SpecialPlanet.ARTIFACT)
    FacilityFactory(planet="planet_d", level=FacilityLevel.BASIC, facility_type=FacilityType.LABORATORY)
    FacilityFactory(planet="planet_d", level=FacilityLevel.ADVANCED, facility_type=FacilityType.LABORATORY)

    planet_a_rp = planetCrud.get_rp_production(session, "planet_a")
    planet_b_rp = planetCrud.get_rp_production(session, "planet_b")
    planet_c_rp = planetCrud.get_rp_production(session, "planet_c")
    planet_d_rp = planetCrud.get_rp_production(session, "planet_d")

    assert planet_a_rp == 0
    assert planet_b_rp == 1
    assert planet_c_rp == 7
    assert planet_d_rp == 7


def test_get_mp_production(session):
    # No facilities
    PlanetFactory(name="planet_a", resources=5)

    # Single basic factory, low value world
    PlanetFactory(name="planet_b", resources=2)
    FacilityFactory(planet="planet_b", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)

    # Multiple factories of various levels on mid-value world
    PlanetFactory(name="planet_c", resources=4)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.INTERMEDIATE, facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.ADVANCED, facility_type=FacilityType.FACTORY)

    # Multiple factories of various levels on a high-value world
    PlanetFactory(name="planet_d", resources=6)
    FacilityFactory(planet="planet_d", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_d", level=FacilityLevel.ADVANCED, facility_type=FacilityType.FACTORY)

    planet_a_mp = planetCrud.get_mp_production(session, "planet_a")
    planet_b_mp = planetCrud.get_mp_production(session, "planet_b")
    planet_c_mp = planetCrud.get_mp_production(session, "planet_c")
    planet_d_mp = planetCrud.get_mp_production(session, "planet_d")

    assert planet_a_mp == 0
    assert planet_b_mp == 2
    assert planet_c_mp == 24
    assert planet_d_mp == 24


def test_get_resource_production__invalid_resource(session):
    PlanetFactory(name="planet_a")

    with pytest.raises(ValueError) as error_info:
        planetCrud.get_resource_production(session, "planet_a", "not a resource")

    assert str(error_info.value) == "Only 'mp', 'rp', and 'lp' are valid resource types."


def test_get_resource_production__non_existent_planet(session):
    PlanetFactory(name="planet_a")

    with pytest.raises(ValueError) as error_info:
        planetCrud.get_resource_production(session, "not_a_planet", "mp")

    assert str(error_info.value) == "Planet 'not_a_planet' does not exist"


def test_get_max_garrison_points(session):
    # TODO: Include a planet with shields, without shields, and an empty planet
    # Planet without any facilities
    PlanetFactory(name="planet_a")

    # Planet with facilities and no shields
    PlanetFactory(name="planet_b")
    FacilityFactory(planet="planet_b", facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_b", facility_type=FacilityType.LABORATORY)

    # Planet with facilities and basic shields
    PlanetFactory(name="planet_c")
    FacilityFactory(planet="planet_c", facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_c", facility_type=FacilityType.LABORATORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.PLANETARY_SHIELDS)

    # Planet with facilities and stacked Intermediate/Advanced shields
    # Planet with facilities and basic shields
    PlanetFactory(name="planet_d")
    FacilityFactory(planet="planet_d", facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_d", facility_type=FacilityType.LABORATORY)
    FacilityFactory(planet="planet_d", level=FacilityLevel.INTERMEDIATE, facility_type=FacilityType.PLANETARY_SHIELDS)
    FacilityFactory(planet="planet_d", level=FacilityLevel.ADVANCED, facility_type=FacilityType.PLANETARY_SHIELDS)

    planet_a_max_garrison = planetCrud.get_max_garrison_points(session, "planet_a")
    planet_b_max_garrison = planetCrud.get_max_garrison_points(session, "planet_b")
    planet_c_max_garrison = planetCrud.get_max_garrison_points(session, "planet_c")
    planet_d_max_garrison = planetCrud.get_max_garrison_points(session, "planet_d")

    assert planet_a_max_garrison == 0
    assert planet_b_max_garrison == 2
    assert planet_c_max_garrison == 4
    assert planet_d_max_garrison == 10


def test_reduce_garrison_points(session):
    # TODO: Include a query that doesn't set amount_to_reduce and one that makes the garrison points negative
    PlanetFactory(name="planet_a", garrison_points=4)
    PlanetFactory(name="planet_b", garrison_points=4)
    PlanetFactory(name="planet_c", garrison_points=4)

    planetCrud.reduce_garrison_points(session, "planet_a", 2)
    planetCrud.reduce_garrison_points(session, "planet_b", 10)  # reducing more than max should be acceptable
    planetCrud.reduce_garrison_points(session, "planet_c")      # default reduction is 1

    planet_a = planetCrud.get_planet_by_name(session, "planet_a")
    planet_b = planetCrud.get_planet_by_name(session, "planet_b")
    planet_c = planetCrud.get_planet_by_name(session, "planet_c")

    assert planet_a.garrison_points == 2
    assert planet_b.garrison_points == -6
    assert planet_c.garrison_points == 3


def test_get_planet_facilities(session):
    # Planet with no facilities
    PlanetFactory(name="planet_a")

    # Planet with one facility
    PlanetFactory(name="planet_b")
    FacilityFactory(planet="planet_b", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)

    # Planet with multiple facilities
    PlanetFactory(name="planet_c")
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.LABORATORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FLEET_HQ)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.DEFENSE_GRID)

    planet_a_facilities = planetCrud.get_planet_facilities(session, "planet_a")
    planet_b_facilities = planetCrud.get_planet_facilities(session, "planet_b")
    planet_c_facilities = planetCrud.get_planet_facilities(session, "planet_c")

    assert list(map(str, planet_a_facilities)) == []
    assert list(map(str, planet_b_facilities)) == ['BF']
    assert list(map(str, planet_c_facilities)) == ['BF', 'BF', 'BL', 'BQ', 'BD']


def test_has_facilities(session):
    # Planet with no facilities
    PlanetFactory(name="planet_a")

    # Planet with one facility
    PlanetFactory(name="planet_b")
    FacilityFactory(planet="planet_b", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)

    # Planet with multiple facilities
    PlanetFactory(name="planet_c")
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FACTORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.LABORATORY)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.FLEET_HQ)
    FacilityFactory(planet="planet_c", level=FacilityLevel.BASIC, facility_type=FacilityType.DEFENSE_GRID)

    assert not planetCrud.has_facilities(session, "planet_a", {'BF'})
    assert not planetCrud.has_facilities(session, "planet_a", {'BF', 'BR', 'IR'})

    assert planetCrud.has_facilities(session, "planet_b", {'BF'})
    assert not planetCrud.has_facilities(session, "planet_b", {'BL'})
    assert planetCrud.has_facilities(session, "planet_b", {'BF', 'AQ'})  # Should be true if ANY in the set exist

    assert planetCrud.has_facilities(session, "planet_c", {'BF'})
    assert planetCrud.has_facilities(session, "planet_c", {'BF', 'BL', 'BQ', 'BD'})
    assert planetCrud.has_facilities(session, "planet_c", {'BF', 'IR'})  # Should be true if ANY in the set exist
    assert not planetCrud.has_facilities(session, "planet_c", {'IR'})
