from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db import get_db
from models import Farmer, Farm
from schemas import FarmerOut, FarmerDetail, FarmBrief

router = APIRouter()


@router.get("/farmers", response_model=list[FarmerOut])
def list_farmers(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Farmer)
        .order_by(Farmer.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        FarmerOut(
            id=f.id,
            name=f.name,
            village=f.village.name if f.village else None,
            joined_date=f.joined_date,
        )
        for f in rows
    ]


@router.get("/farmers/{farmer_id}", response_model=FarmerDetail)
def get_farmer(farmer_id: str, db: Session = Depends(get_db)):
    f = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Farmer not found")
    farms = [
        FarmBrief(
            id=farm.id,
            crop_name=farm.crop.name if farm.crop else "unknown",
            area_hectares=float(farm.area_hectares or 0),
            expected_yield_kg=float(farm.expected_yield_kg or 0),
        )
        for farm in f.farms
    ]
    return FarmerDetail(
        id=f.id,
        name=f.name,
        village=f.village.name if f.village else None,
        joined_date=f.joined_date,
        farms=farms,
    )
