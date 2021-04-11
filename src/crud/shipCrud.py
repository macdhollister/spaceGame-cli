from sqlalchemy.orm import Session

from src import models
from src import schemas

from src.crud import planetCrud

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
    return query_ships_filtered(db, {}).all()


def query_ships_filtered(db: Session, filters: dict):
    return db.query(models.Ship).filter_by(**filters)


def get_visible_ships_on_planet(db: Session, planet_name: str, faction_name: str):
    # TODO clean up this function -- separate out utility methods
    """Gets all ships in orbit of a planet which are visible to a faction"""
    # Maximum stealth level is 10 (10 ECM modules), so all
    # ships are detected if detection level is 11 or above

    effective_detection_level = 0
    visible_ships = []

    planet = planetCrud.get_planet_by_name(db, planet_name)
    ships_on_planet = get_ships_on_planet(db, planet_name)
    ships_owned_by_faction = list(filter(lambda ship: ship.owner == faction_name, ships_on_planet))

    if len(ships_owned_by_faction) > 0:
        effective_detection_level += max(list(map(lambda ship: ship.detection_level, ships_owned_by_faction)))

    planet_has_radar = planetCrud.has_facilities(db, planet_name, {'BR', 'IR', 'AR'})

    if planet.owner == faction_name and planet_has_radar:
        effective_detection_level += 11
    for p in planet.connections:
        if p.owner == faction_name and planetCrud.has_facilities(db, p.name, {'AR'}):
            effective_detection_level += 11

    for ship in ships_on_planet:
        if ship.owner == faction_name or ship.stealth_level <= effective_detection_level:
            visible_ships.append(ship)

    return visible_ships


def get_ships_on_planet(db: Session, planet_name: str):
    return db.query(models.Ship).filter_by(location=planet_name).all()


def get_ship_by_id(db: Session, ship_id: str):
    return db.query(models.Ship).filter_by(id=ship_id).first()


def move_ship(db: Session, ship_id: str, destination_name: str):
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


def retrofit_ship(db: Session, ship_id: str, new_modules: str):
    ship_query = query_ships_filtered(db, {'id': ship_id})
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


def damage_ship(db: Session, ship_id: str, damage: int):
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
