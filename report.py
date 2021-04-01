from sys import argv
from textwrap import dedent

from docopt import docopt

from src.crud import shipCrud, planetCrud, factionCrud
from src.utils import db
from src.utils.facilityUtils import display_facilities
from src.utils.colonyUtils import colony_type_to_str, maximum_facilities
from src.utils.shipUtils import ships_to_str_observed, group_ships_by_faction, ships_to_str_owned

from InquirerPy import inquirer as iq


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

        if empty_facilities > 0:
            facilities.append(f"{empty_facilities} empty")

    facilities_display = display_facilities(facilities)

    ships_on_planet = shipCrud.get_visible_ships_on_planet(database, planet.name, faction_name)
    grouped_ships = group_ships_by_faction(ships_on_planet)

    owned_ships = grouped_ships.pop(faction_name, None)

    owned_ships_display = ""
    if owned_ships is not None:
        owned_ships_display = '\n               '.join(ships_to_str_owned(owned_ships))

    # Owned ships have been removed from 'grouped_ships' via the call to pop() above
    observed_ships_display = '\n               '.join([f"{faction}: {ships_to_str_observed(grouped_ships[faction])}" for faction in grouped_ships.keys()])

    return f"""
           {planet.name} ({size_map[planet.size]}-{planet.resources}) {col_size_display}
           Special: {planet.special.value}
           Owner: {planet_owner}
           Connections: {', '.join(list(map(lambda c: c.name, planet.connections)))}
           Facilities: {facilities_display}
           {owned_ships_display}
           {observed_ships_display}
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


if __name__ == '__main__':
    database = db.get_db()

    kwargs = {
        'db': database,
        '--faction': iq.select(
            message="Faction name:",
            choices=factionCrud.get_faction_names(database)
        ).execute()
    }

    print_report(kwargs)
