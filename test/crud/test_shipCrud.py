from src.crud import shipCrud
from src.utils import shipUtils
from src.utils.facilityUtils import FacilityType, FacilityLevel

from test.conftest import ShipFactory, PlanetFactory, FacilityFactory, FactionFactory, models
import pytest


def ships_to_id_list(ships):
    return sorted(list(map(lambda ship: ship.id, ships)))


def test_validate_module_str():
    assert shipUtils.validate_module_str('S2P1M3S9S8S4')
    assert shipUtils.validate_module_str('B4D6M7B1P8W4H4')
    assert shipUtils.validate_module_str('C1S2P6A5')
    assert shipUtils.validate_module_str('M2')
    assert shipUtils.validate_module_str('D3C8W3P5P4M6')

    assert not shipUtils.validate_module_str('AA5')
    assert not shipUtils.validate_module_str('ASDF')
    assert not shipUtils.validate_module_str('555')
    assert not shipUtils.validate_module_str('m')


def test_get_ships(session):
    ShipFactory(id='a')
    ShipFactory(id='b')
    ShipFactory(id='c')

    assert len(shipCrud.get_ships(session)) == 3


def test_get_ship_by_id(session):
    ShipFactory(id='a', location='planet_a')
    ShipFactory(id='b', location='planet_b')
    ShipFactory(id='c', location='planet_c')

    assert shipCrud.get_ship_by_id(session, 'a').location == 'planet_a'
    assert shipCrud.get_ship_by_id(session, 'b').location == 'planet_b'
    assert shipCrud.get_ship_by_id(session, 'c').location == 'planet_c'


def test_query_ships_filtered(session):
    # Owner, location, modules, id
    ShipFactory(id='a', location='planet_a', owner='faction_1', modules='COLONY')
    ShipFactory(id='b', location='planet_a', owner='faction_1', modules='D1')
    ShipFactory(id='c', location='planet_a', owner='faction_2', modules='COLONY')
    ShipFactory(id='d', location='planet_a', owner='faction_2', modules='D1')

    ShipFactory(id='e', location='planet_b', owner='faction_1', modules='COLONY')
    ShipFactory(id='f', location='planet_b', owner='faction_1', modules='D1')
    ShipFactory(id='g', location='planet_b', owner='faction_2', modules='COLONY')
    ShipFactory(id='h', location='planet_b', owner='faction_2', modules='D1')

    ShipFactory(id='i', location='planet_c', owner='faction_1', modules='COLONY')
    ShipFactory(id='j', location='planet_c', owner='faction_1', modules='D1')
    ShipFactory(id='k', location='planet_c', owner='faction_2', modules='COLONY')
    ShipFactory(id='l', location='planet_c', owner='faction_2', modules='D1')

    ShipFactory(id='m', location='planet_d', owner='faction_1', modules='COLONY')
    ShipFactory(id='n', location='planet_d', owner='faction_1', modules='D1')
    ShipFactory(id='o', location='planet_d', owner='faction_2', modules='COLONY')
    ShipFactory(id='p', location='planet_d', owner='faction_2', modules='D1')

    location_filter = {'location': 'planet_a'}
    owner_filter = {'owner': 'faction_1'}
    colony_filter = {'modules': 'COLONY'}

    def check(filters):
        return ships_to_id_list(shipCrud.query_ships_filtered(session, filters))

    # One at a time
    assert check(location_filter) == ['a', 'b', 'c', 'd']
    assert check(owner_filter) == ['a', 'b', 'e', 'f', 'i', 'j', 'm', 'n']
    assert check(colony_filter) == ['a', 'c', 'e', 'g', 'i', 'k', 'm', 'o']

    # Multiple filters
    assert check(location_filter | owner_filter) == ['a', 'b']
    assert check(location_filter | colony_filter) == ['a', 'c']

    # Ids
    assert check({'id': 'a'}) == ['a']
    assert check({'id': 'b'}) == ['b']


def test_get_visible_ships_on_planet__ship_detection(session):
    # Owned ships present, insufficient detection level
    PlanetFactory(name="planet_a")
    ShipFactory(id="b", owner="faction_1", location="planet_a")
    ShipFactory(id="c", owner="faction_2", location="planet_a", modules="C1")

    # Owned ships present, partially sufficient detection level
    PlanetFactory(name="planet_b")
    ShipFactory(id="d", owner="faction_1", location="planet_b", modules="S1")    # detection level 1
    ShipFactory(id="e", owner="faction_2", location="planet_b", modules="C1")    # stealth level 1 -- detected
    ShipFactory(id="f", owner="faction_2", location="planet_b", modules="C1C1")  # stealth level 2 -- not detected

    # Owned ships present, fully sufficient detection level
    PlanetFactory(name="planet_c")
    ShipFactory(id="g", owner="faction_1", location="planet_c", modules="S1S1")  # detection level 2
    ShipFactory(id="h", owner="faction_2", location="planet_c", modules="C1")    # stealth level 1 -- detected
    ShipFactory(id="i", owner="faction_2", location="planet_c", modules="C1C1")  # stealth level 2 -- detected

    planet_a_ships = shipCrud.get_visible_ships_on_planet(session, "planet_a", "faction_1")
    planet_b_ships = shipCrud.get_visible_ships_on_planet(session, "planet_b", "faction_1")
    planet_c_ships = shipCrud.get_visible_ships_on_planet(session, "planet_c", "faction_1")

    assert ships_to_id_list(planet_a_ships) == ['b']
    assert ships_to_id_list(planet_b_ships) == ['d', 'e']
    assert ships_to_id_list(planet_c_ships) == ['g', 'h', 'i']


def test_get_visible_ships_on_planet__radar_detection(session):
    # Radar on planet
    PlanetFactory(name="planet_d", owner="faction_1")
    FacilityFactory(planet="planet_d", facility_type=FacilityType.RADAR, level=FacilityLevel.BASIC)
    ShipFactory(id="j", owner="faction_2", location="planet_d", modules="C1")
    ShipFactory(id="k", owner="faction_2", location="planet_d", modules="C1C1")

    # Advanced radar adjacent
    planet_e1 = PlanetFactory(name="planet_e1")
    planet_e2 = PlanetFactory(name="planet_e2", owner="faction_1")
    planet_e1.connections = [planet_e2]
    planet_e2.connections = [planet_e1]
    FacilityFactory(planet="planet_e2", facility_type=FacilityType.RADAR, level=FacilityLevel.ADVANCED)
    ShipFactory(id="l", owner="faction_2", location="planet_e1", modules="C1")
    ShipFactory(id="m", owner="faction_2", location="planet_e1", modules="C1C1")

    # Radar present, but planet not owned
    PlanetFactory(name="planet_f")
    FacilityFactory(planet="planet_f", facility_type=FacilityType.RADAR, level=FacilityLevel.BASIC)
    ShipFactory(id="n", owner="faction_1", location="planet_f", modules="D1")
    ShipFactory(id="o", owner="faction_2", location="planet_f", modules="C1")
    ShipFactory(id="p", owner="faction_2", location="planet_f", modules="C1C1")

    planet_d_ships = shipCrud.get_visible_ships_on_planet(session, "planet_d", "faction_1")
    planet_e1_ships = shipCrud.get_visible_ships_on_planet(session, "planet_e1", "faction_1")
    planet_f_ships = shipCrud.get_visible_ships_on_planet(session, "planet_f", "faction_1")

    assert ships_to_id_list(planet_d_ships) == ['j', 'k']
    assert ships_to_id_list(planet_e1_ships) == ['l', 'm']
    assert ships_to_id_list(planet_f_ships) == ['n']


def test_move_ships(session):
    PlanetFactory(name="planet_a")
    PlanetFactory(name="planet_b")
    ShipFactory(id="a", location="planet_a", modules="D1")
    ShipFactory(id="b", location="planet_a", modules="D1")
    ShipFactory(id="c", location="planet_a", modules="D1")

    shipCrud.move_ships(session, ["a", "b", "c"], "planet_b")

    assert shipCrud.get_ship_by_id(session, "a").location == "planet_b"
    assert shipCrud.get_ship_by_id(session, "b").location == "planet_b"
    assert shipCrud.get_ship_by_id(session, "c").location == "planet_b"


def test_move_ships__invalid(session):
    PlanetFactory(name="planet_a")
    PlanetFactory(name="planet_b")
    PlanetFactory(name="planet_c")
    ShipFactory(id="a", location="planet_a", modules="D1")
    ShipFactory(id="b", location="planet_b", modules="D1")
    ShipFactory(id="c", location="planet_a", modules="D1")

    with pytest.raises(ValueError) as error_info:
        shipCrud.move_ships(session, ["a", "b", "c"], "planet_c")

    assert str(error_info.value) == "Ships must have the same origin location."


def test_move_ships__singular(session):
    PlanetFactory(name="planet_a")
    PlanetFactory(name="planet_b")
    ShipFactory(id="a", location="planet_a", modules="D1")

    shipCrud.move_ship(session, "a", "planet_b")

    assert shipCrud.get_ship_by_id(session, "a").location == "planet_b"


def test_create_ship_from_dict(session):
    PlanetFactory(name="planet_a")
    PlanetFactory(name="planet_b")
    FactionFactory(faction_name="faction_1")

    ship_dict_1 = {
        'owner': 'faction_1',
        'modules': 'COLONY',
        'location': 'planet_a'
    }

    ship_dict_2 = {
        'owner': 'faction_1',
        'modules': 'D1W1',
        'location': 'planet_b'
    }

    shipCrud.create_ship_from_dict(session, ship_dict_1)
    shipCrud.create_ship_from_dict(session, ship_dict_2)

    ship_a = session.query(models.Ship).filter_by(location='planet_a').first()
    ship_b = session.query(models.Ship).filter_by(location='planet_b').first()

    assert ship_a.location == 'planet_a'
    assert ship_a.owner == 'faction_1'
    assert ship_a.modules == 'COLONY'

    assert ship_b.location == 'planet_b'
    assert ship_a.owner == 'faction_1'
    assert ship_b.modules == 'D1W1'


def test_retrofit_ship(session):
    ShipFactory(id="ship_a", modules="COLONY")
    ShipFactory(id="ship_b", modules="W1D1")

    # Retrofitting a colony ship
    with pytest.raises(ValueError) as error_info_colony:
        shipCrud.retrofit_ship(session, "ship_a", "W1S1")

    # Retrofitting with invalid modules
    with pytest.raises(ValueError) as error_info_invalid:
        shipCrud.retrofit_ship(session, "ship_b", "Q3Z5")

    # Retrofitting with different number of modules
    with pytest.raises(ValueError) as error_info_length:
        shipCrud.retrofit_ship(session, "ship_b", "D5")

    shipCrud.retrofit_ship(session, "ship_b", "W4S2")

    assert str(error_info_colony.value) == "Cannot retrofit colony ship"
    assert str(error_info_invalid.value) == "New modules 'Q3Z5' includes invalid modules"
    assert str(error_info_length.value) == "Ship 'ship_b' must have exactly 2 modules"
    assert session.query(models.Ship).filter_by(id="ship_b").first().modules == "W4S2"


def test_restore_ship_hp(session):
    ShipFactory(id="ship_a", modules="W1D1", hit_points=1)
    ShipFactory(id="ship_b", modules="D1D1D1", hit_points=1)

    shipCrud.restore_ship_hp(session, "ship_a")
    shipCrud.restore_ship_hp(session, "ship_b")

    assert session.query(models.Ship).filter_by(id="ship_a").first().hit_points == 2
    assert session.query(models.Ship).filter_by(id="ship_b").first().hit_points == 3


def test_restore_all(session):
    ShipFactory(id="ship_a", modules="W1D1", hit_points=1)
    ShipFactory(id="ship_b", modules="D1D1D1", hit_points=1)

    shipCrud.restore_all(session)

    assert session.query(models.Ship).filter_by(id="ship_a").first().hit_points == 2
    assert session.query(models.Ship).filter_by(id="ship_b").first().hit_points == 3


def test_damage_ship(session):
    ShipFactory(id="ship_a", modules="W1D1")
    ShipFactory(id="ship_b", modules="D1D1D1")
    ShipFactory(id="ship_c", modules="W1")
    ShipFactory(id="ship_d", modules="COLONY")

    shipCrud.damage_ship(session, "ship_a")
    shipCrud.damage_ship(session, "ship_b", 2)
    shipCrud.damage_ship(session, "ship_c")
    shipCrud.damage_ship(session, "ship_d")

    assert session.query(models.Ship).filter_by(id="ship_a").first().hit_points == 1
    assert session.query(models.Ship).filter_by(id="ship_b").first().hit_points == 1
    assert session.query(models.Ship).filter_by(id="ship_c").first() is None  # Ship was destroyed
    assert session.query(models.Ship).filter_by(id="ship_d").first() is None  # Ship was destroyed


def test_destroy_ship(session):
    ShipFactory(id="ship_a", modules="W1D1")

    shipCrud.destroy_ship(session, "ship_a")

    assert session.query(models.Ship).filter_by(id="ship_a").first() is None
