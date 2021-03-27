"""
Usage:
    planet.py generate_planets [--planets-file=<string>]
    planet.py print_planets [--faction=<string>]
    planet.py print_single_planet --planet=<string> [--faction=<string>]
    planet.py claim --planet=<string> --faction=<string>
    planet.py damage --planet=<string> [--damage-amount=<integer>]
    planet.py restore --planet=<string>

Options:
    --planets-file=<string>     A json file containing planet information
    --planet=<string>           The name of a planet
    --faction=<string>          The name of a faction
    --damage-amount=<integer>   The number of garrison points to remove from a planet. Defaults to 1.
"""

import json
from sys import argv

from docopt import docopt

from src.crud import planetCrud, shipCrud
from src.utils import db

from textwrap import dedent


def print_planet(database, planet, faction_name=None):
    size_map = {
        's': 'Small',
        'm': 'Medium',
        'l': 'Large'
    }

    col_size_display = ""
    if planet.colony_size and planet.owner:
        max_garrison_points = planetCrud.get_max_garrison_points(database, planet.name)
        col_size_display = f"- {planet.owner} {planet.colony_size} ({planet.garrison_points}/{max_garrison_points} GP)"

    ships_on_planet = \
        shipCrud.get_ships_on_planet(database, planet.name) \
        if faction_name is None \
        else shipCrud.get_visible_ships_on_planet(database, planet.name, faction_name)

    entry = f"""\
            {planet.name} ({size_map[planet.size]}-{planet.resources}) {col_size_display}
            Connections: {', '.join(list(map(lambda c: c.name, planet.connections)))}
            Facilities: {planet.facilities}
            Ships in orbit: {ships_on_planet}
            """
    print(dedent(entry))


def print_single_planet(args):
    planet_name = args['--planet']
    faction_name = args['--faction']
    database = args['db']

    planet_info = planetCrud.get_planet_by_name(database, planet_name)
    print_planet(database, planet_info, faction_name)


def print_planets(args):
    database = args['db']
    faction_name = args['--faction']

    planet_info = planetCrud.get_planets(database)

    for p in planet_info:
        print_planet(database, p, faction_name)


def generate_planets(args):
    if args['--planets-file'] is None:
        args['--planets-file'] = "game_resources/planets.json"

    with open(args['--planets-file']) as f:
        planets_from_file = json.load(f)['planets']

    try:
        planetCrud.build_map(args['db'], planets_from_file)
    # TODO better exception handling
    except Exception:
        print("Could not generate map.")


def claim_planet(args):
    planet_name = args['--planet']
    faction_name = args['--faction']
    database = args['db']
    planetCrud.claim_planet(database, planet_name, faction_name)


def damage_planet(args):
    database = args['db']
    planet_name = args['--planet']
    amount_to_reduce = args['--damage-amount']

    if amount_to_reduce is None:
        planetCrud.reduce_garrison_points(database, planet_name)
    else:
        planetCrud.reduce_garrison_points(database, planet_name, int(amount_to_reduce))


def restore_planet(args):
    database = args['db']
    planet_name = args['--planet']

    planetCrud.restore_garrison_points(database, planet_name)


switcher = {
    'generate_planets': generate_planets,
    'print_planets': print_planets,
    'print_single_planet': print_single_planet,
    'claim': claim_planet,
    'damage': damage_planet,
    'restore': restore_planet
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
