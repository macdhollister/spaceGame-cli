from src.crud import factionCrud
from src.utils.facilityUtils import FacilityLevel, FacilityType

from test.conftest import *


def test_get_resource_income(session):
    FactionFactory(faction_name="faction_1")

    PlanetFactory(name="planet_a", owner="faction_1", resources=1)
    PlanetFactory(name="planet_b", owner="faction_1", resources=2)
    PlanetFactory(name="planet_c", owner="faction_1", resources=3)

    FacilityFactory(planet="planet_a", facility_type=FacilityType.FACTORY, level=FacilityLevel.BASIC)        # 1 mp
    FacilityFactory(planet="planet_a", facility_type=FacilityType.FACTORY, level=FacilityLevel.ADVANCED)     # 3 mp

    FacilityFactory(planet="planet_b", facility_type=FacilityType.LABORATORY, level=FacilityLevel.BASIC)     # 1 rp
    FacilityFactory(planet="planet_b", facility_type=FacilityType.LABORATORY, level=FacilityLevel.ADVANCED)  # 4 rp

    FacilityFactory(planet="planet_c", facility_type=FacilityType.LABORATORY, level=FacilityLevel.BASIC)     # 1 rp
    FacilityFactory(planet="planet_c", facility_type=FacilityType.FACTORY, level=FacilityLevel.ADVANCED)     # 9 mp

    assert factionCrud.get_resource_income(session, "faction_1", "mp") == 13
    assert factionCrud.get_resource_income(session, "faction_1", "rp") == 6


def test_set_research(session):
    FactionFactory(faction_name="faction_1")

    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().research['armor_plating'] == 1

    factionCrud.set_research(session, "faction_1", module_name="armor_plating", tech_level=5)

    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().research['armor_plating'] == 5


def test_get_research(session):
    default_research = {
        "armor_plating": 1,
        "command_bridge": 2,
        "ecm_suite": 3,
        "warp_drive": 4,
        "hangar_bay": 5,
        "marine_barracks": 6,
        "point_defense_battery": 7,
        "sensor_array": 8,
        "heavy_weapons_bay": 9
    }

    FactionFactory(faction_name="faction_1", research=default_research)

    faction_1_research = factionCrud.get_research(session, "faction_1")

    assert faction_1_research['armor_plating'] == 1
    assert faction_1_research['command_bridge'] == 2
    assert faction_1_research['ecm_suite'] == 3
    assert faction_1_research['warp_drive'] == 4
    assert faction_1_research['hangar_bay'] == 5
    assert faction_1_research['marine_barracks'] == 6
    assert faction_1_research['point_defense_battery'] == 7
    assert faction_1_research['sensor_array'] == 8
    assert faction_1_research['heavy_weapons_bay'] == 9


def test_update_resources(session):
    FactionFactory(faction_name="faction_1", mp=10, rp=10)
    PlanetFactory(name="planet_a", resources=5, owner="faction_1")
    FacilityFactory(facility_type=FacilityType.FACTORY, planet="planet_a")
    FacilityFactory(facility_type=FacilityType.LABORATORY, planet="planet_a")

    factionCrud.update_resources(session, "faction_1")

    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().mp == 15
    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().rp == 11


def test_spend_resource(session):
    FactionFactory(faction_name="faction_1", mp=50, rp=20)

    factionCrud.spend_resource(session, "faction_1", "mp", 10)
    factionCrud.spend_resource(session, "faction_1", "rp", 10)

    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().mp == 40
    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().rp == 10


def test_set_resource(session):
    FactionFactory(faction_name="faction_1", mp=50, rp=20, lp=5)

    factionCrud.set_resource(session, "faction_1", "mp", 90)
    factionCrud.set_resource(session, "faction_1", "rp", 30)
    factionCrud.set_resource(session, "faction_1", "lp", 7)

    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().mp == 90
    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().rp == 30
    assert session.query(models.Faction).filter_by(faction_name="faction_1").first().lp == 7


def test_get_faction_names(session):
    FactionFactory(faction_name="faction_1")
    FactionFactory(faction_name="faction_2")

    assert factionCrud.get_faction_names(session) == ["faction_1", "faction_2"]
