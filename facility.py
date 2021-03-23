"""
Usage:
    facility.py create --planet=<string> --type=<string>
    facility.py upgrade --planet=<string> --type=<string> --level=<string>
    facility.py upgrade --planet=<string> --facility-designation=<string>

Options:
    --planet=<string>               The name of the planet that the facility is on
    --type=<string>                 A designation (name or abbreviation) of a facility
    --level=<string>                The level of a facility (basic, intermediate, advanced or abbreviations of those) of a facility
    --facility-designation=<string> Full abbreviated designation for a facility (e.g. BF or IY)
"""

from sys import argv

from docopt import docopt

from src.crud import facilityCrud
from src.utils import db
from src.utils.FacilityEnums import FacilityType, FacilityLevel

from textwrap import dedent


facilities_types_str_to_enum = {
    "factory": FacilityType.FACTORY,
    "f": FacilityType.FACTORY,
    "laboratory": FacilityType.LABORATORY,
    "l": FacilityType.LABORATORY,
    "shipyard": FacilityType.SHIPYARD,
    "y": FacilityType.SHIPYARD,
    "radar": FacilityType.RADAR,
    "r": FacilityType.RADAR,
    "defense_grid": FacilityType.DEFENSE_GRID,
    "d": FacilityType.DEFENSE_GRID,
    "fleet_hq": FacilityType.FLEET_HQ,
    "q": FacilityType.FLEET_HQ,
    "planetary_shields": FacilityType.PLANETARY_SHIELDS,
    "p": FacilityType.PLANETARY_SHIELDS
}

facilities_levels_str_to_enum = {
    "basic": FacilityLevel.BASIC,
    "b": FacilityLevel.BASIC,
    "intermediate": FacilityLevel.INTERMEDIATE,
    "i": FacilityLevel.INTERMEDIATE,
    "advanced": FacilityLevel.ADVANCED,
    "a": FacilityLevel.ADVANCED
}


def create_facility(args):
    database = args['db']
    planet_name = args['--planet']
    facility_type = facilities_types_str_to_enum.get(args['--type'].lower())

    facility = {
        'planet': planet_name,
        'facility_type': facility_type
    }

    facilityCrud.create_facility_from_dict(database, facility)


def upgrade_facility(args):
    database = args['db']
    planet = args['--planet']
    facility_designation = args['--facility-designation']
    if facility_designation is not None:
        facility_split = list(facility_designation)
        level = facility_split[0].lower()
        facility_type = facility_split[1].lower()
    else:
        level = args['--level']
        facility_type = args['--type']

    level = facilities_levels_str_to_enum.get(level)
    facility_type = facilities_types_str_to_enum.get(facility_type)

    facilityCrud.upgrade_facility(database, planet, level, facility_type)


switcher = {
    'create': create_facility,
    'upgrade': upgrade_facility
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
