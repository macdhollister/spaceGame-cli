"""
Usage:
    generate_map.py --planets-file=<string>

Options:
    --planets-file=<string>     A json file containing planet information
"""

import json

from docopt import docopt

from src.crud import planet
from src.utils import db


def main(kwargs):
    database = db.get_db()
    with open(kwargs['--planets-file']) as f:
        planets_from_file = json.load(f)['planets']

    all_planets = planet.build_map(database, planets_from_file)

    for p in all_planets:
        print(p)


if __name__ == '__main__':
    kwargs = docopt(__doc__)
    main(kwargs)
