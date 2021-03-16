from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .Base import Base
from .Faction import Faction
from .Planet import Planet


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)
    modules = Column(String)
    owner = Column(String, ForeignKey(Faction.faction_name))
    location = Column(String, ForeignKey(Planet.name))

    owner_relationship = relationship(Faction, back_populates='ships')
    location_relationship = relationship(Planet, back_populates='ships')

    def __repr__(self):
        return f'{{"id": "{self.id}","owner": "{self.owner}","modules": "{self.modules}"}}'
