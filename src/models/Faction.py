from sqlalchemy import Boolean, Column, Integer, String, PickleType
from sqlalchemy.orm import relationship

from src.utils.db import generate_id
from .Base import Base


class Faction(Base):
    __tablename__ = 'Faction'

    id = Column(String, primary_key=True, index=True, default=generate_id)
    faction_name = Column(String, unique=True, index=True)
    faction_alias = Column(String, unique=True, index=True, default="")
    mp = Column(Integer, default=40)
    rp = Column(Integer, default=25)
    lp = Column(Integer, default=2)

    research = Column(PickleType, default={
        "armor_plating": 1,
        "command_bridge": 1,
        "ecm_suite": 1,
        "warp_drive": 1,
        "hangar_bay": 1,
        "marine_barracks": 1,
        "point_defense_battery": 1,
        "sensor_array": 1,
        "heavy_weapons_bay": 1
    })

    is_active = Column(Boolean, default=True)

    ships = relationship('Ship', back_populates="owner_relationship")
    planets = relationship('Planet', back_populates="owner_relationship")
    # turns = relationship('Turn', back_populates="faction_relationship")

    def __repr__(self):
        return '<Faction(name="%s")>' % self.faction_name
