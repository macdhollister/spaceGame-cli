from src.crud import planetCrud
from src.models import *

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


def test_generate_planets(session):
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
