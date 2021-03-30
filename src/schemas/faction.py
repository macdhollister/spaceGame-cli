from typing import List

from pydantic import BaseModel

from src.schemas.ship import Ship
from src.schemas.planet import Planet
# from src.schemas.turn import Turn


class FactionBase(BaseModel):
    faction_name: str
    faction_alias: str = ""


class FactionCreate(FactionBase):
    pass


class Faction(FactionBase):
    id: int
    mp: int
    rp: int
    lp: int
    is_active: bool
    ships: List[Ship] = []
    planets: List[Planet] = []
    # turns: List[Turn] = []
