from typing import List

from pydantic import BaseModel

from src.schemas.ship import Ship
# from src.schemas.turn import Turn


class FactionBase(BaseModel):
    faction_name: str


class FactionCreate(FactionBase):
    pass


class Faction(FactionBase):
    id: int
    mp: int
    rp: int
    lp: int
    is_active: bool
    ships: List[Ship] = []
    # turns: List[Turn] = []
