"""
Usage:
    facility.py create --planet=<string> --type=<string>
    facility.py upgrade --planet=<string> --facility-id=<integer>

Options:
    --planet=<string>           The name of the planet that the facility is on
    --type=<string>             A designation (name or abbreviation) of a facility
    --facility-id=<integer>     The unique identifier for a facility
"""

from sys import argv

from docopt import docopt

from src.crud import facilityCrud
from src.utils import db
from src.utils.FacilityEnums import FacilityType

from textwrap import dedent


facilities_str_to_enum = {
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


def create_facility(args):
    database = args['db']
    planet_name = args['--planet']
    facility_type = facilities_str_to_enum.get(args['--type'].lower())

    facility = {
        'planet': planet_name,
        'facility_type': facility_type
    }

    facilityCrud.create_facility_from_dict(database, facility)


def upgrade_facility(args):
    pass


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
