from pydantic import BaseModel


class ShipBase(BaseModel):
    owner: str
    modules: str
    location: str


class ShipCreate(ShipBase):
    pass


class Ship(ShipBase):
    id: int
