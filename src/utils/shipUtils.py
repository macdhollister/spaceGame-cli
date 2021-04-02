from collections import Counter

from src.crud import shipCrud

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


def get_ship_choices_on_planet(database, planet_name):
    ships = shipCrud.get_ships_on_planet(database, planet_name)
    options = []

    for ship in ships:
        options.append(ship_to_str_full(ship))


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

    display = ""
    for ship_type in ship_types:
        display += f"class {ship_type} x{counts[ship_type]}"

    return display
