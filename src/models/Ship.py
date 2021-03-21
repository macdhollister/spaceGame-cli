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


def count_module(context, module):
    modules = context.get_current_parameters()['modules']
    return modules.count(module)


def get_stealth_level(context):
    return count_module(context, 'C')  # C represents an ecm suite


def get_detection_level(context):
    return count_module(context, 'S')  # S represents a sensor array


class Ship(Base):
    __tablename__ = 'Ship'

    id = Column(Integer, primary_key=True, index=True)
    modules = Column(String)
    owner = Column(String, ForeignKey(Faction.faction_name))
    location = Column(String, ForeignKey(Planet.name))

    max_hp = Column(Integer, default=get_size)
    hit_points = Column(Integer, default=get_size)
    stealth_level = Column(Integer, default=get_stealth_level)
    detection_level = Column(Integer, default=get_detection_level)

    owner_relationship = relationship(Faction, back_populates='ships')
    location_relationship = relationship(Planet, back_populates='ships')

    def __repr__(self):
        return f'Ship<id: {self.id}, owner: {self.owner}, modules: {self.modules}>'
