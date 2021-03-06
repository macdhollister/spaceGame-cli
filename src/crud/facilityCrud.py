from sqlalchemy.orm import Session

from src import models, schemas
from src.crud import planetCrud
from src.utils.facilityUtils import FacilityType, FacilityLevel


def query_facility_by_id(db: Session, facility_id: str):
    return db.query(models.Facility).filter_by(id=facility_id)


def get_facilities(db: Session):
    return db.query(models.Facility).all()


def query_facilities_on_planet(db: Session, planet_name: str):
    return db.query(models.Facility).filter_by(planet=planet_name)


def create_facility_from_dict(db: Session, facility):
    try:
        db_facility = schemas.FacilityCreate.parse_obj(facility)
    except ValueError:
        errors = []
        if facility['facility_type'] not in set(item.value for item in FacilityType):
            errors.append(f"{facility['facility_type']} is not a valid FacilityType")

        if facility['planet'] not in planetCrud.get_planet_names(db):
            errors.append(f"Planet '{facility['planet']}' does not exist")

        raise ValueError(", ".join(errors))

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


def upgrade_facility(db: Session, facility_id: str):
    facility_query = query_facility_by_id(db, facility_id)
    facility = facility_query.first()
    facility_level = facility.level

    if facility_level == FacilityLevel.BASIC:
        facility.level = FacilityLevel.INTERMEDIATE
    elif facility_level == FacilityLevel.INTERMEDIATE:
        facility.level = FacilityLevel.ADVANCED
    else:
        raise ValueError("Only basic and intermediate facilities can be upgraded.")

    facility_query.update({'level': facility.level})
    db.commit()


def downgrade_facility(db: Session, facility_id: str):
    facility_query = query_facility_by_id(db, facility_id)
    facility = facility_query.first()
    facility_level = facility.level

    if facility_level == FacilityLevel.ADVANCED:
        facility.level = FacilityLevel.INTERMEDIATE
    elif facility_level == FacilityLevel.INTERMEDIATE:
        facility.level = FacilityLevel.BASIC
    elif facility_level == FacilityLevel.BASIC:
        destroy_facility(db, facility_id)
        return

    facility_query.update({'level': facility.level})
    db.commit()


def damage_facility(db: Session, facility_id: str):
    facility = query_facility_by_id(db, facility_id).first()
    current_shields = facility.shields

    if current_shields == 0:
        downgrade_facility(db, facility_id)
    else:
        query_facility_by_id(db, facility_id).update({'shields': current_shields - 1})
    db.commit()


def destroy_facility(db: Session, facility_id: str):
    query_facility_by_id(db, facility_id).delete()
    db.commit()


def get_shield_contribution(facility):
    if facility.facility_type != FacilityType.PLANETARY_SHIELDS:
        return 0

    if facility.level == FacilityLevel.BASIC:
        return 1
    elif facility.level == FacilityLevel.INTERMEDIATE:
        return 2
    elif facility.level == FacilityLevel.ADVANCED:
        return 3


def get_planet_shield_points(db: Session, planet_name: str):
    all_facilities = planetCrud.get_planet_facilities(db, planet_name)
    shield_point_list = list(map(lambda fac: get_shield_contribution(fac), all_facilities))
    return sum(shield_point_list)


def set_facility_shields(db: Session, facilities, total_shields: int):
    for facility in facilities:
        query_facility_by_id(db, facility.id).update({'shields': total_shields})

    db.commit()


def restore_planet_facilities(db: Session, planet_name: str):
    facilities = planetCrud.get_planet_facilities(db, planet_name)
    total_shields = get_planet_shield_points(db, planet_name)

    set_facility_shields(db, facilities, total_shields)


def restore_single_facility(db: Session, facility_id: str):
    facility = query_facility_by_id(db, facility_id).first()
    total_shields = get_planet_shield_points(db, facility.planet)

    set_facility_shields(db, facility, total_shields)
