from typing import List

from pydantic import BaseModel

from .ship import Ship


class PlanetBase(BaseModel):
    pass


class PlanetCreate(PlanetBase):
    name: str
    size: str
    resources: int


class Planet(PlanetBase):
    id: int
    owner: str = None
    connections: List['Planet'] = []
    ships: List[Ship] = []


# Update forward refs to allow Planet class to self reference
Planet.update_forward_refs()
