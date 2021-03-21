from pydantic import BaseModel

from src.utils.FacilityEnums import FacilityLevel, FacilityType


class FacilityBase(BaseModel):
    level: FacilityLevel = FacilityLevel.BASIC
    facility_type: FacilityType
    planet: str


class FacilityCreate(FacilityBase):
    pass


class Facility(FacilityBase):
    id: int
