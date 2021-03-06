from pydantic import BaseModel

from src.utils.facilityUtils import FacilityLevel, FacilityType


class FacilityBase(BaseModel):
    level: FacilityLevel = FacilityLevel.BASIC
    facility_type: FacilityType
    planet: str


class FacilityCreate(FacilityBase):
    pass


class Facility(FacilityBase):
    id: str
