from src.crud import planetCrud
from src.models import Planet

from src.utils.planetUtils import SpecialPlanet
from test.conftest import PlanetFactory


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
