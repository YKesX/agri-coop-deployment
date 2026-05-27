from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db
from models import Village, Farmer
from schemas import VillageOut

router = APIRouter()


@router.get("/villages", response_model=list[VillageOut])
def list_villages(db: Session = Depends(get_db)):
    rows = (
        db.query(Village.id, Village.name, func.count(Farmer.id).label("farmer_count"))
        .outerjoin(Farmer, Farmer.village_id == Village.id)
        .group_by(Village.id, Village.name)
        .order_by(Village.name)
        .all()
    )
    return [VillageOut(id=r.id, name=r.name, farmer_count=r.farmer_count) for r in rows]
