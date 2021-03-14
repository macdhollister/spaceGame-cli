from sqlalchemy import Table, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .Base import Base

connection = Table(
    'PlanetConnection', Base.metadata,
    Column('planet_a_id', Integer, ForeignKey('planets.id'), index=True),
    Column('planet_b_id', Integer, ForeignKey('planets.id')),
    UniqueConstraint('planet_a_id', 'planet_b_id', name='unique_connections')
)


class Planet(Base):
    __tablename__ = 'planets'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    size = Column(String)
    resources = Column(Integer)

    connections = relationship('Planet',
                               secondary=connection,
                               primaryjoin=id == connection.c.planet_a_id,
                               secondaryjoin=id == connection.c.planet_b_id
                               )

    def make_connection(self, other):
        if other not in self.connections:
            self.connections.append(other)
            other.connections.append(self)

    def __repr__(self):
        return '<Planet(name="%s", connections="%s")>' % (self.name, list(map(lambda c: c.name, self.connections)))
