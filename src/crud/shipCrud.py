from sqlalchemy.orm import Session

from src import models
from src import schemas
from src.utils import shipUtils


def get_ships(db: Session):
    return query_ships_filtered(db, {}).all()


def get_ship_by_id(db: Session, ship_id: str):
    return db.query(models.Ship).filter_by(id=ship_id).first()


def query_ships_filtered(db: Session, filters: dict):
    return db.query(models.Ship).filter_by(**filters)


def get_visible_ships_on_planet(db: Session, planet_name: str, faction_name: str):
    """Gets all ships in orbit of a planet which are visible to a faction"""

    effective_detection_level = shipUtils.determine_effective_detection_level(db, planet_name, faction_name)
    visible_ships = []

    ships_on_planet = get_ships_on_planet(db, planet_name)

    for ship in ships_on_planet:
        if ship.owner == faction_name or ship.stealth_level <= effective_detection_level:
            visible_ships.append(ship)

    return visible_ships


def get_ships_on_planet(db: Session, planet_name: str):
    return db.query(models.Ship).filter_by(location=planet_name).all()


def move_ship(db: Session, ship_id: str, destination_name: str):
    ship = db.query(models.Ship).filter_by(id=ship_id)
    ship.update({'location': destination_name})
    db.commit()
    return ship


def create_ship(db: Session, ship: schemas.ShipCreate):
    if ship.modules == "COLONY":
        return create_colony_ship(db, ship)

    if not shipUtils.validate_module_str(ship.modules):
        raise ValueError("The modules string is invalid. Must match the regex ^([ABCDHMPSW][1-9]){1,10}$")

    db_ship = models.Ship(
        owner=ship.owner,
        modules=ship.modules,
        location=ship.location
    )
    db.add(db_ship)
    db.commit()
    db.refresh(db_ship)
    return db_ship


def create_colony_ship(db: Session, ship: schemas.ShipCreate):
    db_ship = models.Ship(
        owner=ship.owner,
        modules="COLONY",
        location=ship.location
    )
    db.add(db_ship)
    db.commit()
    return db_ship


def create_ship_from_dict(db: Session, ship):
    create_ship(db, schemas.ShipCreate.parse_obj(ship))


def retrofit_ship(db: Session, ship_id: str, new_modules: str):
    ship_query = query_ships_filtered(db, {'id': ship_id})

    ship_current = ship_query.first()
    size = shipUtils.get_size(ship_current)

    if ship_current.modules == "COLONY":
        raise ValueError("Cannot retrofit colony ship")

    if len(new_modules)/2 != size:
        raise ValueError(f"Ship '{ship_id}' must have exactly {size} modules")

    if not shipUtils.validate_module_str(new_modules):
        raise ValueError(f"New modules '{new_modules}' includes invalid modules")

    ship_query.update({'modules': new_modules})
    db.commit()


def restore_ship_hp_without_commit(db: Session, ship_id: str):
    max_hp = get_ship_by_id(db, ship_id).max_hp
    db.query(models.Ship).filter_by(id=ship_id).update({'hit_points': max_hp})


def restore_ship_hp(db: Session, ship_id: str):
    restore_ship_hp_without_commit(db, ship_id)
    db.commit()


def restore_all(db: Session):
    ships = db.query(models.Ship).all()

    for ship in ships:
        restore_ship_hp_without_commit(db, ship.id)

    db.commit()


def damage_ship(db: Session, ship_id: str, damage: int = 1):
    ship_to_damage = get_ship_by_id(db, ship_id)
    damaged_hp = ship_to_damage.hit_points - damage

    if damaged_hp <= 0:
        destroy_ship(db, ship_id)
    else:
        db.query(models.Ship).filter_by(id=ship_id).update({'hit_points': damaged_hp})
        db.commit()


def destroy_ship(db: Session, ship_id: str):
    ship_to_delete = get_ship_by_id(db, ship_id)

    db.query(models.Ship).filter_by(id=ship_id).delete()
    db.commit()
    return ship_to_delete
