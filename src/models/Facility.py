from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship

from src.utils.FacilityEnums import FacilityType, FacilityLevel
from .Base import Base
from .Planet import Planet


facility_type_to_str = {
    FacilityType.FACTORY: 'F',
    FacilityType.LABORATORY: 'L',
    FacilityType.SHIPYARD: 'Y',
    FacilityType.RADAR: 'R',
    FacilityType.DEFENSE_GRID: 'D',
    FacilityType.FLEET_HQ: 'Q',
    FacilityType.PLANETARY_SHIELDS: 'P'
}

facility_level_to_str = {
    FacilityLevel.BASIC: 'B',
    FacilityLevel.INTERMEDIATE: 'I',
    FacilityLevel.ADVANCED: 'A'
}


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
        return f'{facility_level_to_str.get(self.level)}{facility_type_to_str.get(self.facility_type)}'
