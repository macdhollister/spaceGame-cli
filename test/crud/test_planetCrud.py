from src.crud import planetCrud
from src.utils.colonyUtils import ColonyType
from src.utils.facilityUtils import FacilityLevel, FacilityType

from src.utils.planetUtils import SpecialPlanet
from test.conftest import *


def test_generate_planets(session):
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
