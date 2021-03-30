"""
Usage:
    report.py generate_report --faction=<string>

Options:
    --faction=<string>      Name of a faction to generate a report for

"""

from sys import argv
from textwrap import dedent

from docopt import docopt

from src.crud import shipCrud, planetCrud, factionCrud
from src.utils import db
from src.utils.colonyUtils import colony_type_to_str, maximum_facilities


def generate_resources_section(args):
    database = args['db']
    faction_name = args['--faction']

    faction = factionCrud.query_faction_by_name(database, faction_name).first()

    rp_total = faction.rp
    mp_total = faction.mp

    rp_income = factionCrud.get_resource_income(database, faction_name, "rp")
    mp_income = factionCrud.get_resource_income(database, faction_name, "mp")
    lp_income = factionCrud.get_resource_income(database, faction_name, "lp")

    return dedent(f"""\
           ------------------------
           Available Resources
           ------------------------
           {rp_total} Research Points (Income: {rp_income})
           {mp_total} Material Points (Income: {mp_income})
           {lp_income} Logistics Points
           """)


def generate_module_research_section(args):
    database = args['db']
    faction_name = args['--faction']

    faction = factionCrud.query_faction_by_name(database, faction_name).first()
    research = faction.research

    armor_research = research['armor_plating']
    bridge_research = research['command_bridge']
    ecm_research = research['ecm_suite']
    warp_drive_research = research['warp_drive']
    hangar_research = research['hangar_bay']
    point_defense_research = research['point_defense_battery']
    sensor_research = research['sensor_array']
    barracks_research = research['marine_barracks']
    heavy_weapons_research = research['heavy_weapons_bay']

    return dedent(f"""\
           ------------------------
           Ship Module Research
           ------------------------
           Armor (A): {armor_research}
           Bridge (B): {bridge_research}
           ECM (C): {ecm_research}
           Warp Drive (D): {warp_drive_research}
           Hangar (H): {hangar_research}
           Point Defense (P): {point_defense_research}
           Sensor (S): {sensor_research}
           Barracks (M): {barracks_research}
           Heavy Weapons (W): {heavy_weapons_research}
           """)


def get_planet_entry(database, planet, faction_name):
    size_map = {
        's': 'Small',
        'm': 'Medium',
        'l': 'Large'
    }

    facilities = [fac.__repr__() for fac in planet.facilities]

    col_size_display = ""
    planet_owner = "unclaimed"
    num_facilities = len(facilities)
    if planet.colony_size and planet.owner:
        max_garrison_points = planetCrud.get_max_garrison_points(database, planet.name)
        col_size_display = f"- {colony_type_to_str.get(planet.colony_size)} ({planet.garrison_points}/{max_garrison_points} GP)"
        planet_owner = planet.owner

        max_facilities = maximum_facilities.get(planet.colony_size)
        empty_facilities = max_facilities - num_facilities

        facilities.append(f"{empty_facilities} empty")

    ships_on_planet = shipCrud.get_visible_ships_on_planet(database, planet.name, faction_name)

    return f"""
           {planet.name} ({size_map[planet.size]}-{planet.resources}) {col_size_display}
           Special: {planet.special.value}
           Owner: {planet_owner}
           Connections: {', '.join(list(map(lambda c: c.name, planet.connections)))}
           Facilities: {facilities}
           Ships in orbit: {ships_on_planet}
           """


def get_planet_entries(database, planets, faction_name):
    entries = []
    for planet in planets:
        entries.append(get_planet_entry(database, planet, faction_name))

    return '\n'.join(entries)


def generate_planets_section(args):
    database = args['db']
    faction_name = args['--faction']

    planets_in_report = planetCrud.get_planets_by_faction(database, faction_name)

    return dedent(f"""\
           ------------------------
           Controlled Planets
           ------------------------
           {get_planet_entries(database, planets_in_report['controlled'], faction_name)}

           ------------------------
           Observed Planets
           ------------------------
           {get_planet_entries(database, planets_in_report['observed'], faction_name)}
           """)


def print_report(args):
    resources_section = generate_resources_section(args)
    module_research_section = generate_module_research_section(args)
    planets_section = generate_planets_section(args)

    print(resources_section)
    print(module_research_section)
    print(planets_section)


switcher = {
    'generate_report': print_report
}

if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()

    # Accounting for faction name aliases as soon as possible
    if '--faction' in kwargs:
        db_faction = factionCrud.query_faction_by_name(kwargs['db'], kwargs['--faction']).first()
        kwargs['--faction'] = db_faction.faction_name

    method = argv[1]
    switcher.get(method)(kwargs)
