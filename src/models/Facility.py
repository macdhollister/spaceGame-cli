from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship

from src.utils.FacilityEnum import FacilityType, FacilityLevel, type_to_abbreviated_str, level_to_abbreviated_str
from .Base import Base
from .Planet import Planet


class Facility(Base):
    __tablename__ = 'Facility'

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(FacilityLevel), default=FacilityLevel.BASIC)
    facility_type = Column(Enum(FacilityType))
    planet = Column(String, ForeignKey(Planet.name))

    is_blockaded = Column(Boolean, default=False)
    shields = Column(Integer, default=0)

    planet_relationship = relationship(Planet, back_populates='facilities')

    def __repr__(self):
        return f'{level_to_abbreviated_str.get(self.level)}{type_to_abbreviated_str.get(self.facility_type)}'
