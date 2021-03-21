from sqlalchemy.orm import Session

from src import models
from src import schemas

from src.crud import shipCrud


def get_planets(db: Session):
    return db.query(models.Planet).all()


def get_planet_by_id(db: Session, planet_id: int):
    return db.query(models.Planet).filter_by(id=planet_id).first()


def get_planet_by_name(db: Session, planet_name: str):
    return query_planet_by_name(db, planet_name).first()


def query_planet_by_name(db: Session, planet_name: str):
    return db.query(models.Planet).filter_by(name=planet_name)


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


def planet_visible_by_faction(db: Session, planet_name: str, faction_name: str):
    # Visible if the planet is owned by the faction or if the faction has ships on it
    planet = get_planet_by_name(db, planet_name)
    faction_owns_planet = planet.owner == faction_name

    all_ships_on_planet = shipCrud.get_ships_on_planet(db, planet_name)
    faction_has_ship = faction_name in list(map(lambda ship: ship.owner, all_ships_on_planet))

    return faction_owns_planet | faction_has_ship


# ---------- FACILITIES ----------

def get_planet_facilities(db: Session, planet_name: str):
    return get_planet_by_name(db, planet_name).facilities


def has_facilities(db: Session, planet_name: str, facilities_set: set):
    """Takes a set of facility designations and returns a boolean
    depending on if the planet has any of those facilities"""
    return len(
        facilities_set & set(map(lambda fac: fac['facility_designation'], get_planet_facilities(db, planet_name)))
    ) > 0
