"""
Usage:
    ship.py create --planet=<string> --faction=<string> --modules=<string>
    ship.py destroy --ship-id=<integer>
    ship.py damage --ship-id=<integer> [--damage=<integer>]
    ship.py restore --ship-id=<integer>
    ship.py restore_all
    ship.py move --ship-id=<integer> --destination=<string>
    ship.py get_all

Options:
    --planet=<string>       The planet on which to create the ship
    --faction=<string>      The owner of the ship
    --modules=<string>      The modules on the ship. Should match the regex ^([ABCDHMPSWabcdhmpsw][1-9]){1,10}$
    --ship-id=<integer>     The unique identifier for a ship
    --destination=<string>  The location a ship is to be moved
    --damage=<integer>      (optional) Amount of damage to inflict to a ship. Defaults to 1 damage.
"""

from sys import argv

from docopt import docopt

from src.crud import shipCrud, factionCrud
from src.utils import db

from textwrap import dedent


def create_ship(args):
    planet = args['--planet']
    faction = args['--faction']
    modules = args['--modules']
    database = args['db']

    ship = {
        'owner': faction,
        'modules': modules,
        'location': planet
    }

    shipCrud.create_ship_from_dict(database, ship)


def destroy_ship(args):
    ship_id = args['--ship-id']
    database = args['db']

    shipCrud.destroy_ship(database, ship_id)


def move_ship(args):
    destination = args['--destination']
    ship_id = args['--ship-id']
    database = args['db']

    shipCrud.move_ship(database, ship_id, destination)


def damage_ship(args):
    ship_id = args['--ship-id']
    damage = args['--damage'] if args['--damage'] is not None else 1
    database = args['db']

    shipCrud.damage_ship(database, ship_id, int(damage))


def restore_ship(args):
    ship_id = args['--ship-id']
    database = args['db']

    shipCrud.restore_ship_hp(database, ship_id)


def restore_all(args):
    database = args['db']

    shipCrud.restore_all(database)


def get_all(args):
    database = args['db']

    all_ships = shipCrud.get_ships(database)
    for ship in all_ships:
        display = f"""\
                id: {ship.id}
                owner: {ship.owner}
                modules: {ship.modules}
                location: {ship.location}
                stealth level: {ship.stealth_level}
                detection level: {ship.detection_level}
                
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
    kwargs['db'] = db.get_db()

    # Accounting for faction name aliases as soon as possible
    if '--faction' in kwargs:
        db_faction = factionCrud.query_faction_by_name(kwargs['db'], kwargs['--faction']).first()
        kwargs['--faction'] = db_faction.faction_name

    method = argv[1]
    switcher.get(method)(kwargs)
