from sqlalchemy.orm import Session

from src import models, schemas
from src.utils.FacilityEnums import FacilityType, FacilityLevel

from src.crud import planetCrud


def get_facilities(db: Session):
    return db.query(models.Facility).all()


def create_facility_from_dict(db: Session, facility):
    db_facility = schemas.FacilityCreate.parse_obj(facility)
    create_facility(db, db_facility)


def create_facility(db: Session, facility: schemas.FacilityCreate):
    planet_owner = planetCrud.get_planet_by_name(db, facility.planet).owner
    if planet_owner is None:
        raise ValueError("Cannot create facility on un-claimed planet.")

    db_facility = models.Facility(
        facility_type=facility.facility_type,
        planet=facility.planet
    )
    db.add(db_facility)
    db.commit()


def upgrade_facility(db: Session, facility_id: int):
    facility_query = db.query(models.Facility).filter_by(id=facility_id)
    facility = facility_query.first()
    facility_level = facility.level

    if facility_level == FacilityLevel.BASIC:
        facility.level = FacilityLevel.INTERMEDIATE
    elif facility_level == FacilityLevel.INTERMEDIATE:
        facility.level = FacilityLevel.ADVANCED
    else:
        raise ValueError("Only basic and intermediate facilities can be upgraded.")

    facility_query.update(level=facility.level)
