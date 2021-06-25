"""
Usage:
    faction.py generate_factions [--db_url=<string>]
    faction.py update_research [--db_url=<string>]
    faction.py update_resource [--db_url=<string>]
    faction.py spend_resource [--db_url=<string>]
    faction.py update_all_resources [--db_url=<string>]
    faction.py print_factions [--db_url=<string>]
"""

import json
from sys import argv
from textwrap import dedent

from InquirerPy import inquirer as iq
from docopt import docopt

from src.crud import factionCrud
from src.utils import db
from src.utils.db import Database
from src.utils.factionUtils import resource_types
from src.utils.shipUtils import module_types


def generate_factions(database):
    factions_file = "game_resources/factions.json"
    use_default_path = iq.confirm("Use default path? (game_resources/factions.json)").execute()
    if not use_default_path:
        factions_file = iq.text("Factions file location:").execute()

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


def print_factions(database):
    faction_info = factionCrud.get_factions(database)

    for f in faction_info:
        print_single_faction(f)


def update_research(database):
    faction_name = iq.select(
        message="Faction name:",
        choices=factionCrud.get_faction_names(database)
    ).execute()
    module_name = iq.select(
        message="Module name:",
        choices=module_types
    ).execute()
    tech_level = int(iq.text(
        message="Tech level:",
        validate=lambda level: 0 < int(level) < 10,
        invalid_message="Research has a maximum of 10.",
    ).execute())

    factionCrud.set_research(database, faction_name, module_name, tech_level)


def update_resource(database):
    faction_name = iq.select(
        message="Faction name:",
        choices=factionCrud.get_faction_names(database)
    ).execute()
    resource = iq.select(
        message="Resource type:",
        choices=resource_types
    ).execute()
    new_total = int(iq.text("New total:").execute())

    factionCrud.set_resource(database, faction_name, resource, new_total)


def spend_resource(database):
    faction_name = iq.select(
        message="Faction name:",
        choices=factionCrud.get_faction_names(database)
    ).execute()
    resource = iq.select(
        message="Resource type:",
        choices=resource_types
    ).execute()
    amount = int(iq.text("Amount spent:").execute())

    factionCrud.spend_resource(database, faction_name, resource, amount)


def update_all_resources(database):
    do_update_all_factions = iq.confirm("Update all factions?").execute()
    faction_name = None
    if not do_update_all_factions:
        faction_name = iq.text("Faction name:").execute()

    factions = list(map(lambda fac: fac.faction_name, factionCrud.get_factions(database)))\
        if faction_name is None\
        else [faction_name]

    for faction in factions:
        factionCrud.update_resources(database, faction)


switcher = {
    'generate_factions': generate_factions,
    'print_factions': print_factions,
    'update_research': update_research,
    'update_resource': update_resource,
    'spend_resource': spend_resource,
    'update_all_resources': update_all_resources
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    db = Database(kwargs['--db_url']).get_db()

    method = argv[1]
    switcher.get(method)(db)
