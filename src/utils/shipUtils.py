import re
from collections import Counter

from sqlalchemy.orm import Session

from src.crud import shipCrud, planetCrud

module_types = [
    'armor_plating',
    'command_bridge',
    'ecm_suite',
    'warp_drive',
    'hangar_bay',
    'marine_barracks',
    'point_defense_battery',
    'sensor_array',
    'heavy_weapons_bay'
]


module_abbreviations = {
    'armor_plating': 'A',
    'command_bridge': 'B',
    'ecm_suite': 'C',
    'warp_drive': 'D',
    'hangar_bay': 'H',
    'marine_barracks': 'M',
    'point_defense_battery': 'P',
    'sensor_array': 'S',
    'heavy_weapons_bay': 'W'
}


module_options = [
    {"name": '(A) Armor Plating', "value": 'armor_plating'},
    {"name": '(B) Command Bridge', "value": 'command_bridge'},
    {"name": '(C) ECM Suite', "value": 'ecm_suite'},
    {"name": '(D) Warp Drive', "value": 'warp_drive'},
    {"name": '(H) Hangar Bay', "value": 'hangar_bay'},
    {"name": '(M) Marine Barracks', "value": 'marine_barracks'},
    {"name": '(P) Point Defense Battery', "value": 'point_defense_battery'},
    {"name": '(S) Sensor Array', "value": 'sensor_array'},
    {"name": '(W) Heavy Weapons Bay', "value": 'heavy_weapons_bay'}
]


def get_ship_choices_on_planet(db: Session, planet_name: str):
    ships = shipCrud.get_ships_on_planet(db, planet_name)
    options = []

    for ship in ships:
        options.append(ship_to_str_full(ship))


def determine_effective_detection_level(db: Session, planet_name: str, faction_name: str):
    """Determines what level of stealth a faction can detect on a given planet"""
    # Maximum stealth level is 10 (10 ECM modules), so all
    # ships are detected if detection level is 11 or above

    effective_detection_level = 0

    planet = planetCrud.get_planet_by_name(db, planet_name)
    ships_on_planet = shipCrud.get_ships_on_planet(db, planet_name)
    ships_owned_by_faction = list(filter(lambda ship: ship.owner == faction_name, ships_on_planet))

    if len(ships_owned_by_faction) > 0:
        effective_detection_level += max(list(map(lambda ship: ship.detection_level, ships_owned_by_faction)))

    planet_has_radar = planetCrud.has_facilities(db, planet_name, {'BR', 'IR', 'AR'})

    if planet.owner == faction_name and planet_has_radar:
        effective_detection_level += 11
    for p in planet.connections:
        if p.owner == faction_name and planetCrud.has_facilities(db, p.name, {'AR'}):
            effective_detection_level += 11

    return effective_detection_level


def get_ships_with_factions(ships):
    grouped_ships = group_ships_by_faction(ships)

    for faction in grouped_ships.keys():
        grouped_ships[faction] = list(map(lambda ship: get_size(ship), grouped_ships[faction]))

    return grouped_ships


def group_ships_by_faction(ships):
    factions = {}
    for ship in ships:
        if ship.owner not in factions:
            factions[ship.owner] = [ship]
        else:
            factions[ship.owner].append(ship)

    return factions


def get_size(ship):
    if ship.modules == "COLONY":
        return 1

    return int(len(ship.modules) / 2)


def ship_to_str_full(ship):
    return f"<id: {ship.id}, {ship.modules}>"


def ships_to_str_owned(ship_list):
    ships = list(map(ship_to_str_full, ship_list))
    ships.insert(0, "Owned Ships:")

    return ships


def ships_to_str_observed(ship_list):
    ship_list = list(map(lambda ship: get_size(ship), ship_list))

    counts = Counter(ship_list)

    ship_types = list(counts.keys())
    ship_types.sort()

    ships_to_display = []
    for ship_type in ship_types:
        ships_to_display.append(f"class {ship_type} x{counts[ship_type]}")

    return ', '.join(ships_to_display)


def validate_module_str(modules_str):
    pattern = re.compile("^([ABCDHMPSWabcdhmpsw][1-9]){1,10}$")  # Example: W1D2M5
    return bool(re.match(pattern, modules_str))
