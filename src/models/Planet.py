from sqlalchemy import Table, Column, Integer, String, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship

from src.utils.colonyUtils import ColonyType
from src.utils.db import generate_id
from src.utils.planetUtils import SpecialPlanet
from .Base import Base
from .Faction import Faction

connection = Table(
    'PlanetConnection', Base.metadata,
    Column('planet_a_id', String, ForeignKey('Planet.id'), index=True),
    Column('planet_b_id', String, ForeignKey('Planet.id')),
    UniqueConstraint('planet_a_id', 'planet_b_id', name='unique_connections')
)


class Planet(Base):
    __tablename__ = 'Planet'

    id = Column(String, primary_key=True, index=True, default=generate_id)
    name = Column(String, unique=True, index=True)
    size = Column(String)
    special = Column(Enum(SpecialPlanet), default=SpecialPlanet.STANDARD)

    colony_size = Column(Enum(ColonyType), default=None)
    resources = Column(Integer)
    owner = Column(String, ForeignKey(Faction.faction_name), nullable=True)
    garrison_points = Column(Integer, default=0)

    connections = relationship('Planet',
                               secondary=connection,
                               primaryjoin=id == connection.c.planet_a_id,
                               secondaryjoin=id == connection.c.planet_b_id
                               )
    ships = relationship('Ship', back_populates="location_relationship")
    facilities = relationship('Facility', back_populates="planet_relationship")

    owner_relationship = relationship(Faction, back_populates='planets')

    def make_connection(self, other):
        if other not in self.connections:
            self.connections.append(other)
            other.connections.append(self)

    def __repr__(self):
        return '<Planet(name="%s", connections="%s")>' % (self.name, list(map(lambda c: c.name, self.connections)))
