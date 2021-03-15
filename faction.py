"""
Usage:
    faction.py generate_factions --factions-file=<string>
    faction.py print_factions

Options:
    --factions-file=<string>        A json file containing faction information
"""

import json
from sys import argv

from docopt import docopt

from src.crud import factionCrud
from src.utils import db


def generate_factions(args):
    with open(args['--factions-file']) as f:
        factions_from_file = json.load(f)['factions']

    factionCrud.build_factions(args['db'], factions_from_file)


def print_factions(args):
    faction_info = factionCrud.get_factions(args['db'])

    for f in faction_info:
        entry = '%s\nmp: %s\nrp: %s\nlp: %s\n' % (
            f.faction_name,
            f.mp,
            f.rp,
            f.lp
        )
        print(entry)


switcher = {
    'generate_factions': generate_factions,
    'print_factions': print_factions
}


if __name__ == '__main__':
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
