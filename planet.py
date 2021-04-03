"""
Usage:
    planet.py generate_planets
    planet.py print_planets
    planet.py print_single_planet
    planet.py claim
    planet.py colonize
    planet.py upgrade
    planet.py damage
    planet.py restore
"""

import json
from sys import argv

from docopt import docopt

from src.utils.colonyUtils import colony_type_to_str
from src.crud import planetCrud, shipCrud, factionCrud
from src.utils import db, planetUtils, promptUtils

from textwrap import dedent

from InquirerPy import inquirer as iq


def get_planet_entry(database, planet, faction_name=None):
    size_map = {
        's': 'Small',
        'm': 'Medium',
        'l': 'Large'
    }

    col_size_display = ""
    if planet.colony_size and planet.owner:
        max_garrison_points = planetCrud.get_max_garrison_points(database, planet.name)
        col_size_display = f"- {planet.owner} {colony_type_to_str.get(planet.colony_size)} ({planet.garrison_points}/{max_garrison_points} GP)"

    ships_on_planet = \
        shipCrud.get_ships_on_planet(database, planet.name) \
        if faction_name is None \
        else shipCrud.get_visible_ships_on_planet(database, planet.name, faction_name)

    entry = f"""\
            {planet.name} ({size_map[planet.size]}-{planet.resources}) {col_size_display}
            Special: {planet.special.value}
            Connections: {', '.join(list(map(lambda c: c.name, planet.connections)))}
            Facilities: {planet.facilities}
            Ships in orbit: {ships_on_planet}
            """
    return dedent(entry)


def print_planet(database, planet, faction_name=None):
    print(get_planet_entry(database, planet, faction_name))


def print_single_planet(database):
    planet_name = promptUtils.planet_prompt(database)

    print_for_faction = iq.confirm("Print for specific faction?").execute()

    if print_for_faction:
        faction_name = iq.select(
            message="Faction:",
            choices=factionCrud.get_faction_names(database)
        ).execute()
    else:
        faction_name = None

    planet_info = planetCrud.get_planet_by_name(database, planet_name)
    print_planet(database, planet_info, faction_name)


def print_planets(database):
    print_for_faction = iq.confirm("Print for specific faction?").execute()

    if print_for_faction:
        faction_name = iq.select(
            message="Faction:",
            choices=factionCrud.get_faction_names(database)
        ).execute()
    else:
        faction_name = None

    planet_info = planetCrud.get_planets(database)

    for p in planet_info:
        print_planet(database, p, faction_name)


def generate_planets(database):
    planets_file_path = "game_resources/planets.json"
    use_default_path = iq.confirm(f"Use default path? ({planets_file_path})").execute()
    if not use_default_path:
        planets_file_path = iq.text("Planets file location:").execute()

    errors = planetUtils.validate_planets_file(planets_file_path)
    if len(errors) > 0:
        return print('\n'.join(errors))

    with open(planets_file_path) as f:
        planets_from_file = json.load(f)['planets']

    try:
        planetCrud.build_map(database, planets_from_file)
    # TODO better exception handling
    except Exception:
        print("Could not generate map.")


def claim_planet(database):
    planet_name = promptUtils.planet_prompt(database)
    faction_name = iq.select(
        message="Faction:",
        choices=factionCrud.get_faction_names(database)
    ).execute()

    planetCrud.claim_planet(database, planet_name, faction_name)


def colonize_planet(database):
    pass


def upgrade_planet(database):
    planet_name = promptUtils.planet_prompt(database)

    planetCrud.upgrade_colony_type(database, planet_name)


def damage_planet(database):
    planet_name = promptUtils.planet_prompt(database)
    amount_to_reduce = int(iq.text("Garrison points lost:").execute())

    if amount_to_reduce is None:
        planetCrud.reduce_garrison_points(database, planet_name)
    else:
        planetCrud.reduce_garrison_points(database, planet_name, int(amount_to_reduce))


def restore_planet(database):
    planet_name = promptUtils.planet_prompt(database)

    planetCrud.restore_garrison_points(database, planet_name)


switcher = {
    'generate_planets': generate_planets,
    'print_planets': print_planets,
    'print_single_planet': print_single_planet,
    'claim': claim_planet,
    'colonize': colonize_planet,
    'upgrade': upgrade_planet,
    'damage': damage_planet,
    'restore': restore_planet
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    db = db.get_db()

    method = argv[1]
    switcher.get(method)(db)
