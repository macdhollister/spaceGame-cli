"""
Usage:
    ship.py create --planet=<string> --faction=<string> --modules=<string>
    ship.py destroy --ship_id=<integer>

Options:
    --planet=<string>       The planet on which to create the ship
    --faction=<string>      The owner of the ship
    --modules=<string>      The modules on the ship. Should match the regex ^([ABCDHMPSW][1-9]){1,10}$
    --ship_id=<integer>     The unique identifier for a ship
"""

from sys import argv

from docopt import docopt

from src.crud import shipCrud
from src.utils import db


def create_ship(args):
    # planet = args['--planet']
    faction = args['--faction']
    modules = args['--modules']
    database = args['db']

    ship = {
        'owner': faction,
        'modules': modules
    }

    shipCrud.create_ship_from_dict(database, ship)


def destroy_ship(args):
    ship_id = args['--ship-id']
    database = args['db']

    shipCrud.destroy_ship(database, ship_id)


def move_ship(args):
    pass


switcher = {
    'create': create_ship,
    'destroy': destroy_ship,
    'move': move_ship
}


if __name__ == '__main__':
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)