"""
Usage:
    ship.py create
    ship.py destroy
    ship.py damage
    ship.py restore
    ship.py restore_all
    ship.py move
    ship.py get_all
"""

from sys import argv
from textwrap import dedent

from InquirerPy import inquirer as iq
from docopt import docopt

from src.crud import shipCrud, factionCrud, planetCrud
from src.utils import db
from src.utils.shipUtils import module_types, module_abbreviations


def create_ship(database):
    # TODO: Clean up this method, pull out utility methods

    planet_name = iq.text("Planet:").execute()
    faction_name = iq.select(
        message="Faction:",
        choices=factionCrud.get_faction_names(database)
    ).execute()

    faction_research = factionCrud.get_research(database, faction_name)

    ship_size = iq.select(
        message="Class:",
        choices=[
            {"name": "Colony ship", "value": "COLONY"},
            {"name": "Class 1", "value": 1},
            {"name": "Class 2", "value": 2},
            {"name": "Class 3", "value": 3},
            {"name": "Class 4", "value": 4},
            {"name": "Class 5", "value": 5},
            {"name": "Class 6", "value": 6},
            {"name": "Class 7", "value": 7},
            {"name": "Class 8", "value": 8},
            {"name": "Class 9", "value": 9},
            {"name": "Class 10", "value": 10}
        ]
    ).execute()

    if ship_size == "COLONY":
        return shipCrud.create_ship_from_dict(database, {
            'owner': faction_name,
            'modules': ship_size,
            'location': planet_name
        })

    module_array = []

    for i in range(ship_size):
        module_type = iq.select(
            message="Module type:",
            choices=module_types
        ).execute()

        module_abbreviation = module_abbreviations.get(module_type)

        module_level = str(faction_research.get(module_type))

        module_array.append(module_abbreviation + module_level)

    modules = ''.join(module_array)

    ship = {
        'owner': faction_name,
        'modules': modules,
        'location': planet_name
    }

    shipCrud.create_ship_from_dict(database, ship)


def destroy_ship(database):
    ship_id = iq.text("Ship id:").execute()

    shipCrud.destroy_ship(database, ship_id)


def move_ship(database):
    origin_location = iq.text("From:").execute()

    ships_on_origin = shipCrud.get_ships_on_planet(database, origin_location)
    ship_ids_on_origin = list(map(lambda ship: f"{ship.id}, modules: {ship.modules}, owner: {ship.owner}", ships_on_origin))

    ship_selection = iq.select(
        message="Ship:",
        choices=ship_ids_on_origin
    ).execute()

    ship_id = ship_selection.split(',')[0]

    origin_connections = planetCrud.get_connection_names(database, origin_location)

    destination = iq.select(
        message="Destination:",
        choices=origin_connections
    ).execute()

    shipCrud.move_ship(database, ship_id, destination)


def damage_ship(database):
    ship_id = iq.text("Ship id:").execute()
    damage = int(iq.text("Damage:").execute())

    shipCrud.damage_ship(database, ship_id, damage)


def restore_ship(database):
    ship_id = iq.text("Ship id:").execute()

    shipCrud.restore_ship_hp(database, ship_id)


def restore_all(database):
    shipCrud.restore_all(database)


def get_all(database):
    query_filters = {}

    do_filter_by_planet = iq.confirm("Filter by planet?").execute()
    if do_filter_by_planet:
        query_filters['location'] = iq.text("Planet:").execute()

    do_filter_by_faction = iq.confirm("Filter by faction?").execute()
    if do_filter_by_faction:
        query_filters['owner'] = iq.select(
            message="Faction:",
            choices=factionCrud.get_faction_names(database)
        ).execute()

    all_ships = shipCrud.query_ships_filtered(database, query_filters).all()
    for ship in all_ships:
        display = f"""\
                id: {ship.id}
                owner: {ship.owner}
                modules: {ship.modules}
                location: {ship.location}
                stealth level: {ship.stealth_level}
                detection level: {ship.detection_level}
                hit points: {ship.hit_points}
                
                """
        print(dedent(display))


switcher = {
    'create': create_ship,
    'destroy': destroy_ship,
    'move': move_ship,
    'damage': damage_ship,
    'restore': restore_ship,
    'restore_all': restore_all,
    'get_all': get_all
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    db = db.get_db()

    method = argv[1]
    switcher.get(method)(db)
