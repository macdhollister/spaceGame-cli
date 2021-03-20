from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .Base import Base
from .Faction import Faction
from .Planet import Planet


def get_size(context):
    if context.get_current_parameters()['modules'] == "COLONY":
        return 1
    else:
        return len(context.get_current_parameters()['modules']) / 2


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)
    modules = Column(String)
    owner = Column(String, ForeignKey(Faction.faction_name))
    location = Column(String, ForeignKey(Planet.name))
    max_hp = Column(Integer, default=get_size)
    hit_points = Column(Integer, default=get_size)

    owner_relationship = relationship(Faction, back_populates='ships')
    location_relationship = relationship(Planet, back_populates='ships')

    def __repr__(self):
        return f'{{"id": "{self.id}","owner": "{self.owner}","modules": "{self.modules}"}}'
