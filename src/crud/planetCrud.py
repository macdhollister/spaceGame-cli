from sqlalchemy.orm import Session

from src import models
from src import schemas


def get_planets(db: Session):
    return db.query(models.Planet).all()


def count_facility_type(facility_list, facility_designation):
    count = 0
    for facility in facility_list:
        if facility['facility_designation'] == facility_designation:
            count += 1

    return count


def build_facility(db: Session, planet_name: str, facility_designation: str):
    facilities_query = db.query(models.Planet).filter_by(name=planet_name)
    facilities = facilities_query.first().facilities

    num_basic_shields = count_facility_type(facilities, "BP")
    num_intermediate_shields = count_facility_type(facilities, "IP")
    num_advanced_shields = count_facility_type(facilities, "AP")

    facility_hp = max(2 * num_basic_shields + 3 * num_intermediate_shields + 4 * num_advanced_shields, 1)

    new_facility = {
        'facility_designation': facility_designation,
        'hit_points': facility_hp
    }

    facilities.append(new_facility)

    if facility_designation in ["BP", "IP", "AP"]:
        for facility in facilities:
            hp_to_add = {
                "BP": 2,
                "IP": 3,
                "AP": 4
            }[facility_designation]

            facility['hit_points'] += hp_to_add

    facilities_query.update({'facilities': facilities})
    db.commit()


def destroy_facility(db: Session, planet_name: str, facility_type: str):
    pass


def claim_planet(db: Session, planet_name: str, faction_name: str):
    planet = db.query(models.Planet).filter_by(name=planet_name)
    if planet.first().owner:
        reassign_planet(db, planet, faction_name)
    else:
        colonize_planet(db, planet, faction_name)


def reassign_planet(db: Session, planet, faction_name: str):
    planet.update({'owner': faction_name})
    db.commit()


def colonize_planet(db: Session, planet, faction_name: str):
    planet.update({'owner': faction_name, 'colony_size': 'Colony'})
    db.commit()


def get_planet_by_id(db: Session, planet_id: int):
    return db.query(models.Planet).filter_by(id=planet_id).first()


def get_planet_by_name(db: Session, planet_name: str):
    return db.query(models.Planet).filter_by(name=planet_name).first()


def create_planet(db: Session, planet: schemas.PlanetCreate):
    db_planet = models.Planet(
        name=planet.name,
        size=planet.size,
        resources=planet.resources
    )
    db.add(db_planet)
    db.commit()
    db.refresh(db_planet)
    return db_planet


def build_map(db: Session, planets):
    for planet in planets:
        create_planet(db, schemas.PlanetCreate.parse_obj(planet))

    for planet in planets:
        db_planet = get_planet_by_name(db, planet['name'])
        for neighbor in planet['connections']:
            db_planet.make_connection(get_planet_by_name(db, neighbor))

        db.commit()
        db.refresh(db_planet)

    return get_planets(db)
