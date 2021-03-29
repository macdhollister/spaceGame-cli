"""
Usage:
    facility.py get_facilities --planet=<string>
    facility.py create --planet=<string> --type=<string> [--blockaded]
    facility.py upgrade --facility-id=<integer> [--blockaded]
    facility.py downgrade --facility-id=<integer>
    facility.py damage --facility-id=<integer>
    facility.py restore_single --facility-id=<integer>
    facility.py restore_all --planet=<string>

Options:
    --planet=<string>               The name of the planet that the facility is on
    --type=<string>                 A designation (name or abbreviation) of a facility
    --facility-id=<integer>         The unique identifier for a facility (can be found via get_facilities method)
    --blockaded                     Takes no argument. Add this flag if the planet is blockaded.
"""

from sys import argv
from textwrap import dedent

from docopt import docopt

from src.crud import facilityCrud, planetCrud
from src.utils import db
from src.utils.FacilityEnum import type_to_enum, type_to_str, level_to_str


def get_facilities(args):
    database = args['db']
    planet_name = args['--planet']

    facilities = facilityCrud.query_facilities_on_planet(database, planet_name).all()

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
    is_blockaded = args['--blockaded']

    facility = {
        'planet': planet_name,
        'facility_type': facility_type
    }

    facilityCrud.create_facility_from_dict(database, facility)

    if not is_blockaded:
        planetCrud.restore_garrison_points(database, planet_name)
        facilityCrud.restore_planet_facilities(database, planet_name)


def upgrade_facility(args):
    database = args['db']
    facility_id = args['--facility-id']
    is_blockaded = args['--blockaded']

    facilityCrud.upgrade_facility(database, facility_id)

    if not is_blockaded:
        planet_name = facilityCrud.query_facility_by_id(database, facility_id).first().planet

        planetCrud.restore_garrison_points(database, planet_name)
        facilityCrud.restore_planet_facilities(database, planet_name)


def downgrade_facility(args):
    database = args['db']
    facility_id = args['--facility-id']

    facilityCrud.downgrade_facility(database, facility_id)


def damage_facility(args):
    database = args['db']
    facility_id = args['--facility-id']

    facilityCrud.damage_facility(database, facility_id)


def restore_single_facility(args):
    database = args['db']
    facility_id = args['--facility-id']

    facilityCrud.restore_single_facility(database, facility_id)


def restore_planet_facilities(args):
    database = args['db']
    planet_name = args['--planet']

    facilityCrud.restore_planet_facilities(database, planet_name)


switcher = {
    'create': create_facility,
    'upgrade': upgrade_facility,
    'downgrade': downgrade_facility,
    'damage': damage_facility,
    'get_facilities': get_facilities,
    'restore_single': restore_single_facility,
    'restore_all': restore_planet_facilities
}


if __name__ == '__main__':
    if len(argv) == 1:
        argv.append('-h')
    kwargs = docopt(__doc__)
    kwargs['db'] = db.get_db()
    method = argv[1]
    switcher.get(method)(kwargs)
