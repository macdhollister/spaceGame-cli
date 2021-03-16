from sqlalchemy.orm import Session

from src import models
from src import schemas


def get_planets(db: Session):
    return db.query(models.Planet).all()


def reassign_planet(db: Session, planet_name: str, faction_name: str):
    planet = db.query(models.Planet).filter_by(name=planet_name)
    planet.update({'owner': faction_name})
    db.commit()
    return planet


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
