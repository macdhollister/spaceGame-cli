from sqlalchemy.orm import Session

from src import models, schemas
from src.utils.FacilityEnums import FacilityType, FacilityLevel

from src.crud import planetCrud

import copy


def query_facility_by_id(db: Session, facility_id: int):
    return db.query(models.Facility).filter_by(id=facility_id)


def get_facilities(db: Session):
    return db.query(models.Facility).all()


def query_facilities_on_planet(db: Session, planet_name: str):
    return db.query(models.Facility).filter_by(planet=planet_name)


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


def downgrade_facility(db: Session, facility_id: int):
    # TODO: Check if shields should reset to full after a facility is downgraded (I think they should)
    facility_query = query_facility_by_id(db, facility_id)
    facility = facility_query.first()
    facility_level = facility.level

    if facility_level == FacilityLevel.ADVANCED:
        facility.level = FacilityLevel.INTERMEDIATE
    elif facility_level == FacilityLevel.INTERMEDIATE:
        facility.level = FacilityLevel.BASIC
    elif facility_level == FacilityLevel.BASIC:
        facility_to_destroy = destroy_facility(db, facility_id)
        return print(f'Destroyed facility {facility_id} ({facility_to_destroy} on {facility_to_destroy.planet})')

    facility_query.update({'level': facility.level})
    db.commit()


def damage_facility(db: Session, facility_id: int):
    facility = query_facility_by_id(db, facility_id).first()

    current_hp = 1 + facility.shields
    new_hp = current_hp - 1

    if new_hp < 1:
        downgrade_facility(db, facility_id)
    else:
        query_facility_by_id(db, facility_id).update({'shields': facility.shields - 1})
    db.commit()


def destroy_facility(db: Session, facility_id: int):
    facility_to_delete = query_facility_by_id(db, facility_id).first()
    facility_copy = copy.deepcopy(facility_to_delete)

    query_facility_by_id(db, facility_id).delete()
    db.commit()
    return facility_copy


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
    shield_point_map = list(map(lambda fac: get_shield_contribution(fac), all_facilities))
    return sum(shield_point_map)


def set_facility_shields(db: Session, facilities, total_shields: int):
    # Note: This intentionally does not commit to the db to support efficiency for bulk updates
    for facility in facilities:
        query_facility_by_id(db, facility.id).update({'shields': total_shields})


def restore_planet_facilities(db: Session, planet_name: str):
    facilities = planetCrud.get_planet_facilities(db, planet_name)
    total_shields = get_planet_shield_points(db, planet_name)

    set_facility_shields(db, facilities, total_shields)

    db.commit()


def restore_single_facility(db: Session, facility_id: int):
    facility = query_facility_by_id(db, facility_id).all()
    total_shields = get_planet_shield_points(db, facility[0].planet)

    set_facility_shields(db, facility, total_shields)

    db.commit()
