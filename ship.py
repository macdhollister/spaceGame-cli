"""
Usage:
    ship.py create --planet=<string> --faction=<string> --modules=<string>
    ship.py destroy --ship-id=<integer>
    ship.py damage --ship-id=<integer> [--damage=<integer>]
    ship.py restore --ship-id=<integer>
    ship.py restore_all
    ship.py move --ship-id=<integer> --destination=<string>

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

from src.crud import shipCrud
from src.utils import db


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


switcher = {
    'create': create_ship,
    'destroy': destroy_ship,
    'move': move_ship,
    'damage': damage_ship,
    'restore': restore_ship,
    'restore_all': restore_all
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
