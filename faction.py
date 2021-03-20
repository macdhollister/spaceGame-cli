"""
Usage:
    faction.py generate_factions [--factions-file=<string>]
    faction.py update_research --faction-name=<string> --module-name=<string> --tech-level=<integer>
    faction.py print_factions

Options:
    --factions-file=<string>        A json file containing faction information
    --faction-name=<string>         Name of a faction
    --module-name=<string>          The name of a ship module, underscores in place of spaces. Options are:
                                    armor_plating, command_bridge, ecm_suite, warp_drive, hangar_bay,
                                    marine_barracks, point_defense_battery, sensor_array, heavy_weapons_bay
    --tech-level=<integer>          The desired tech level to set for a module
"""

import json
from sys import argv

from docopt import docopt

from src.crud import factionCrud
from src.utils import db

from textwrap import dedent


def generate_factions(args):
    if args['--factions-file'] is None:
        args['--factions-file'] = "game_resources/factions.json"

    factions_file = args['--factions-file']
    database = args['db']

    with open(factions_file) as f:
        factions_from_file = json.load(f)['factions']

    factionCrud.build_factions(database, factions_from_file)


def print_single_faction(f):
    entry = f"""\
            ------------------------------
            {f.faction_name}
            ------------------------------
            MP: {f.mp}
            RP: {f.rp}
            LP: {f.lp}
            Research:
                Armor Plating: {f.research['armor_plating']}
                Command Bridge: {f.research['command_bridge']}
                ECM Suite: {f.research['ecm_suite']}
                Warp Drive: {f.research['warp_drive']}
                Hangar Bay: {f.research['hangar_bay']}
                Marine Barracks: {f.research['marine_barracks']}
                Point Defense Battery: {f.research['point_defense_battery']}
                Sensor Array: {f.research['sensor_array']}
                Heavy Weapons Bay: {f.research['heavy_weapons_bay']}
            """

    print(dedent(entry))


def print_factions(args):
    database = args['db']

    faction_info = factionCrud.get_factions(database)

    for f in faction_info:
        print_single_faction(f)


def update_research(args):
    database = args['db']
    faction_name = args['--faction-name']
    module_name = args['--module-name']
    tech_level = int(args['--tech-level'])

    factionCrud.update_research(database, faction_name, module_name, tech_level)


switcher = {
    'generate_factions': generate_factions,
    'print_factions': print_factions,
    'update_research': update_research
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
