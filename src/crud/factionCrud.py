from sqlalchemy.orm import Session

from src import models
from src import schemas
from src.crud import planetCrud
from src.utils.FacilityEnum import FacilityType


def get_resource_income(db: Session, faction_name: str, resource_type: str):
    income = 0

    owned_planets = planetCrud.query_planets_by_owner(db, faction_name).all()

    for planet in owned_planets:
        income += planetCrud.get_resource_production(db, planet.name, resource_type)

    return income


def set_research(db: Session, faction_name: str, module_name: str, tech_level: int):
    faction_query = query_faction_by_name(db, faction_name)
    faction_research = faction_query.first().research
    faction_research[module_name] = tech_level

    faction_query.update({'research': faction_research})
    db.commit()
    return faction_query


def update_resources(db: Session, faction_name: str):
    faction_query = query_faction_by_name(db, faction_name)
    faction = faction_query.first()

    mp_income = get_resource_income(db, faction_name, "mp")
    rp_income = get_resource_income(db, faction_name, "rp")
    lp_income = get_resource_income(db, faction_name, "lp")

    current_mp = faction.mp
    current_rp = faction.rp

    set_resource(db, faction_name, "mp", current_mp + mp_income)
    set_resource(db, faction_name, "rp", current_rp + rp_income)
    set_resource(db, faction_name, "lp", lp_income)


def spend_resource(db: Session, faction_name: str, resource_type: str, amount_spent: int):
    faction_query = query_faction_by_name(db, faction_name)
    faction = faction_query.first()

    # TODO: Pull this out into a util validation
    valid_resources = ['mp', 'rp', 'lp']
    if resource_type not in valid_resources:
        raise ValueError(f"Resource type must be one of {valid_resources}")

    current_holdings = faction[resource_type]

    if amount_spent > current_holdings:
        raise ValueError(f"Amount of {resource_type} spent ({amount_spent}) is higher than the current holdings ({current_holdings})")

    set_resource(db, faction_name, resource_type, current_holdings - amount_spent)


def set_resource(db: Session, faction_name: str, resource: str, new_total: int):
    valid_resources = ['mp', 'lp', 'rp']
    if resource.lower() not in valid_resources:
        raise ValueError("Valid resources are mp, lp, and rp")

    faction_query = query_faction_by_name(db, faction_name)

    faction_query.update({resource: new_total})
    db.commit()


def query_faction_by_name(db: Session, faction_name: str):
    query = db.query(models.Faction).filter_by(faction_name=faction_name)

    if query.first() is None:
        query = db.query(models.Faction).filter_by(faction_alias=faction_name)

    return query


def get_factions(db: Session):
    return db.query(models.Faction).all()


def create_faction(db: Session, faction: schemas.FactionCreate):
    db_faction = models.Faction(
        faction_name=faction.faction_name,
        faction_alias=faction.faction_alias
    )
    db.add(db_faction)
    db.commit()
    db.refresh(db_faction)
    return db_faction


def build_factions(db: Session, factions):
    for faction in factions:
        create_faction(db, schemas.FactionCreate.parse_obj(faction))
