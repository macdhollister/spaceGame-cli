from sqlalchemy.orm import Session

from src import models
from src import schemas


def get_ship_by_id(db: Session, ship_id: int):
    return db.query(models.Ship).filter_by(id=ship_id).first()


def create_ship(db: Session, ship: schemas.ShipCreate):
    db_ship = models.Ship(owner=ship.owner, modules=ship.modules)
    db.add(db_ship)
    db.commit()
    db.refresh(db_ship)
    return db_ship


def create_ship_from_dict(db: Session, ship):
    create_ship(db, schemas.ShipCreate.parse_obj(ship))


def destroy_ship(db: Session, ship_id: int):
    ship_to_delete = get_ship_by_id(db, ship_id)

    models.Ship.filter_by(id=ship_id).delete()
    db.commit()
    return ship_to_delete
