"""
Usage:
    planet.py generate_planets --planets-file=<string>
    planet.py print_planets
    planet.py claim --planet-name=<string> --faction-name=<string>
    planet.py build_facility --planet-name=<string> --facility-designation=<string>
    planet.py destroy_facility --planet-name=<string> --facility-designation=<string>

Options:
    --planets-file=<string>         A json file containing planet information
    --planet-name=<string>          The name of a planet
    --faction-name=<string>         The name of a faction
    --facility-designation=<string> A two character designation for a facility (e.g. BY for basic shipyard)
"""

import json
from sys import argv

from docopt import docopt

from src.crud import planetCrud
from src.utils import db

from textwrap import dedent


def generate_planets(args):
    with open(args['--planets-file']) as f:
        planets_from_file = json.load(f)['planets']

    try:
        planetCrud.build_map(args['db'], planets_from_file)
    # TODO better exception handling
    except Exception:
        print("Could not generate map.")


def print_planets(args):
    planet_info = planetCrud.get_planets(args['db'])

    size_map = {
        's': 'Small',
        'm': 'Medium',
        'l': 'Large'
    }

    for p in planet_info:
        col_size_display = ""
        if p.colony_size and p.owner:
            col_size_display = "- %s %s" % (p.owner, p.colony_size)

        entry = """\
                %s (%s-%s) %s
                Connections: %s
                Facilities: %s
                """ % (
            p.name,
            size_map[p.size],
            p.resources,
            col_size_display,
            ', '.join(list(map(lambda c: c.name, p.connections))),
            p.facilities
        )
        print(dedent(entry))


def claim_planet(args):
    planet_name = args['--planet-name']
    faction_name = args['--faction-name']
    database = args['db']
    planetCrud.claim_planet(database, planet_name, faction_name)


def destroy_facility(args):
    planet_name = args['--planet-name']
    facility_designation = args['--facility-designation']
    database = args['db']
    planetCrud.destroy_facility(database, planet_name, facility_designation)


def build_facility(args):
    planet_name = args['--planet-name']
    facility_designation = args['--facility-designation']
    database = args['db']
    planetCrud.build_facility(database, planet_name, facility_designation)


switcher = {
    'generate_planets': generate_planets,
    'print_planets': print_planets,
    'claim': claim_planet,
    'build_facility': build_facility,
    'destroy_facility': destroy_facility
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
