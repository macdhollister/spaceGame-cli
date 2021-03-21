from sqlalchemy.orm import Session

from src import models
from src import schemas

import re


def get_module_type(module_string):
    module_dict = {
        "A": "Armor Plating",
        "B": "Command Bridge",
        "C": "ECM Suite",
        "D": "Warp Drive",
        "H": "Hangar Bay",
        "M": "Marine Barracks",
        "P": "Point Defense Battery",
        "S": "Sensor Array",
        "W": "Heavy Weapons Bay"
    }

    return module_dict[module_string]


def validate_module_str(modules_str):
    pattern = re.compile("^([ABCDHMPSWabcdhmpsw][1-9]){1,10}$")  # Example: W1D2M5
    return bool(re.match(pattern, modules_str))


def get_modules_from_str(modules_str):
    if not validate_module_str(modules_str):
        raise ValueError("The modules string is invalid. Must match the regex ^([ABCDHMPSW][1-9]){1,10}$")

    modules_array = [modules_str[i:i + 2] for i in range(0, len(modules_str), 2)]
    modules = {}

    for module in modules_array:
        split = list(module)
        module_type = split[0]
        tech_level = split[1]

        if module_type in modules:
            if tech_level != modules[module_type]['tech_level']:
                raise ValueError("Like modules on the same ship must have the same tech level")

            modules[module_type]['quantity'] += 1
        else:
            modules[module_type] = {
                "tech_level": tech_level,
                "quantity": 1
            }
    return modules


def get_ships(db: Session):
    return db.query(models.Ship).all()


def get_ships_on_planet(db: Session, planet_name: str):
    return db.query(models.Ship).filter_by(location=planet_name).all()


def get_ship_by_id(db: Session, ship_id: int):
    return db.query(models.Ship).filter_by(id=ship_id).first()


def move_ship(db: Session, ship_id: int, destination_name: str):
    ship = db.query(models.Ship).filter_by(id=ship_id)
    ship.update({'location': destination_name})
    db.commit()
    return ship


def create_ship(db: Session, ship: schemas.ShipCreate):
    if ship.modules == "COLONY":
        return create_colony_ship(db, ship)

    if not validate_module_str(ship.modules):
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


def restore_ship_hp_without_commit(db: Session, ship_id):
    max_hp = get_ship_by_id(db, ship_id).max_hp
    db.query(models.Ship).filter_by(id=ship_id).update({'hit_points': max_hp})


def restore_ship_hp(db: Session, ship_id: int):
    restore_ship_hp_without_commit(db, ship_id)
    db.commit()


def restore_all(db: Session):
    ships = db.query(models.Ship).all()

    for ship in ships:
        restore_ship_hp_without_commit(db, ship.id)

    db.commit()


def damage_ship(db: Session, ship_id: int, damage: int):
    ship_to_damage = get_ship_by_id(db, ship_id)
    damaged_hp = ship_to_damage.hit_points - damage

    if damaged_hp <= 0:
        destroy_ship(db, ship_id)
    else:
        db.query(models.Ship).filter_by(id=ship_id).update({'hit_points': damaged_hp})
        db.commit()


def destroy_ship(db: Session, ship_id: int):
    ship_to_delete = get_ship_by_id(db, ship_id)

    db.query(models.Ship).filter_by(id=ship_id).delete()
    db.commit()
    return ship_to_delete
