"""
Usage:
    facility.py get_facilities
    facility.py create
    facility.py upgrade
    facility.py downgrade
    facility.py damage
    facility.py restore_single
    facility.py restore_all
"""

from sys import argv
from textwrap import dedent

from InquirerPy import inquirer as iq
from docopt import docopt

from src.crud import facilityCrud, planetCrud
from src.utils import db
from src.utils.facilityUtils import type_to_str, level_to_str, all_facility_types


def get_facilities(database):
    planet_name = iq.text("Planet:").execute()

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


def create_facility(database):

    planet_name = iq.text("Planet:").execute()
    facility_type = iq.select(
        message="Facility type:",
        choices=all_facility_types
    ).execute()
    is_blockaded = iq.confirm("Blockaded?").execute()

    facility = {
        'planet': planet_name,
        'facility_type': facility_type
    }

    facilityCrud.create_facility_from_dict(database, facility)

    if not is_blockaded:
        planetCrud.restore_garrison_points(database, planet_name)
        facilityCrud.restore_planet_facilities(database, planet_name)


def upgrade_facility(database):

    facility_id = iq.text("Facility id:").execute()
    is_blockaded = iq.confirm("Blockaded?").execute()

    facilityCrud.upgrade_facility(database, facility_id)

    if not is_blockaded:
        planet_name = facilityCrud.query_facility_by_id(database, facility_id).first().planet

        planetCrud.restore_garrison_points(database, planet_name)
        facilityCrud.restore_planet_facilities(database, planet_name)


def downgrade_facility(database):
    facility_id = iq.text("Facility id:").execute()

    facilityCrud.downgrade_facility(database, facility_id)


def damage_facility(database):
    facility_id = iq.text("Facility id:").execute()

    facilityCrud.damage_facility(database, facility_id)


def restore_single_facility(database):
    facility_id = iq.text("Facility id:").execute()

    facilityCrud.restore_single_facility(database, facility_id)


def restore_planet_facilities(database):
    planet_name = iq.text("Planet:").execute()

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
    db = db.get_db()

    method = argv[1]
    switcher.get(method)(db)
