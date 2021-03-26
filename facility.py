"""
Usage:
    facility.py get_facilities --planet=<string>
    facility.py create --planet=<string> --type=<string>
    facility.py upgrade --facility-id=<integer>
    facility.py downgrade --facility-id=<integer>
    facility.py damage --facility-id=<integer>

Options:
    --planet=<string>               The name of the planet that the facility is on
    --type=<string>                 A designation (name or abbreviation) of a facility
    --facility-id=<integer>         The unique identifier for a facility (can be found via get_facilities method)
"""

from sys import argv

from docopt import docopt

from src.crud import facilityCrud
from src.utils import db
from src.utils.FacilityEnums import type_to_enum, type_to_str, level_to_str

from textwrap import dedent


def get_facilities(args):
    database = args['db']
    planet_name = args['--planet']

    facilities = facilityCrud.get_facilities_on_planet(database, planet_name)

    print(dedent(f"""\
                 -------------------------------
                 Facilities on {planet_name}
                 -------------------------------\
                 """))

    for facility in facilities:
        entry = f"""\
                id: {facility.id}
                level: {level_to_str.get(facility.level)}
                type: {type_to_str.get(facility.facility_type)}
                HP: {1 + facility.shields}
                """

        print(dedent(entry))


def create_facility(args):
    database = args['db']
    planet_name = args['--planet']
    facility_type = type_to_enum.get(args['--type'].lower())

    facility = {
        'planet': planet_name,
        'facility_type': facility_type
    }

    facilityCrud.create_facility_from_dict(database, facility)


def upgrade_facility(args):
    database = args['db']
    facility_id = args['--facility-id']

    facilityCrud.upgrade_facility(database, facility_id)


def downgrade_facility(args):
    database = args['db']
    facility_id = args['--facility-id']

    facilityCrud.downgrade_facility(database, facility_id)


def damage_facility(args):
    database = args['db']
    facility_id = args['--facility-id']

    facilityCrud.damage_facility(database, facility_id)


switcher = {
    'create': create_facility,
    'upgrade': upgrade_facility,
    'downgrade': downgrade_facility,
    'damage': damage_facility,
    'get_facilities': get_facilities
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
