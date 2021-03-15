from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .Base import Base


class Faction(Base):
    __tablename__ = "factions"

    id = Column(Integer, primary_key=True, index=True)
    faction_name = Column(String, unique=True, index=True)
    mp = Column(Integer, default=40)
    rp = Column(Integer, default=25)
    lp = Column(Integer, default=2)
    is_active = Column(Boolean, default=True)

    ships = relationship('Ship', back_populates="owner_relationship")
    # turns = relationship('Turn', back_populates="faction_relationship")

    def __repr__(self):
        return '<Faction(name="%s")>' % self.faction_name
