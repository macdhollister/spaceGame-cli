"""
Usage:
    map.py generate_map --planets-file=<string>
    map.py print_map

Options:
    --planets-file=<string>     A json file containing planet information
"""

import json
from sys import argv

from docopt import docopt

from src.crud import planetCrud
from src.utils import db


def generate_map(args):
    with open(args['--planets-file']) as f:
        planets_from_file = json.load(f)['planets']

    try:
        planetCrud.build_map(args['db'], planets_from_file)
    # TODO better exception handling
    except Exception:
        print("Could not generate map.")


def print_map(args):
    planet_info = planetCrud.get_planets(args['db'])

    size_map = {
        's': 'small',
        'm': 'medium',
        'l': 'large'
    }

    for p in planet_info:
        entry = '%s (%s-%s)\nConnections: %s\n' % (
            p.name,
            size_map[p.size],
            p.resources,
            ', '.join(list(map(lambda c: c.name, p.connections)))
        )
        print(entry)


switcher = {
    'generate_map': generate_map,
    'print_map': print_map
}


if __name__ == '__main__':
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
