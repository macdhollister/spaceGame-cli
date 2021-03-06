from typing import List

from pydantic import BaseModel

from .ship import Ship
from src.utils.planetUtils import SpecialPlanet


class PlanetBase(BaseModel):
    pass


class PlanetCreate(PlanetBase):
    name: str
    size: str
    resources: int
    special: SpecialPlanet = SpecialPlanet.STANDARD


class Planet(PlanetBase):
    id: str
    owner: str = None
    connections: List['Planet'] = []
    ships: List[Ship] = []


# Update forward refs to allow Planet class to self reference
Planet.update_forward_refs()
