import json

from sqlalchemy.orm import Session

from src import models
from src import schemas


def get_faction(db: Session, faction_id: int):
    db_faction = db.query(models.Faction).filter_by(id=faction_id).first()

    # ships = []
    # for ship in db_faction.ships:
    #     ships.append(json.loads(str(ship)))

    return {
        "id": db_faction.id,
        "faction_name": db_faction.faction_name,
        "is_active": db_faction.is_active,
        # "ships": ships
    }


def get_faction_by_name(db: Session, faction: str):
    return db.query(models.Faction).filter_by(faction_name=faction).first()


def get_factions(db: Session):
    return db.query(models.Faction).all()


def create_faction(db: Session, faction: schemas.FactionCreate):
    db_faction = models.Faction(faction_name=faction.faction_name)
    db.add(db_faction)
    db.commit()
    db.refresh(db_faction)
    return db_faction


def build_factions(db: Session, factions):
    for faction in factions:
        create_faction(db, schemas.FactionCreate.parse_obj(faction))
