from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db
from models import Farm, Farmer, Village, SensorReading
from schemas import YieldByVillage, AvgMoistureByVillage

router = APIRouter()


@router.get("/stats/yield-by-village", response_model=list[YieldByVillage])
def yield_by_village(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Village.name.label("village"),
            func.coalesce(func.sum(Farm.expected_yield_kg), 0).label("total_yield_kg"),
            func.coalesce(func.sum(Farm.area_hectares), 0).label("total_hectares"),
        )
        .join(Farmer, Farmer.village_id == Village.id)
        .join(Farm, Farm.farmer_id == Farmer.id)
        .group_by(Village.name)
        .order_by(Village.name)
        .all()
    )
    return [
        YieldByVillage(
            village=r.village,
            total_yield_kg=float(r.total_yield_kg),
            total_hectares=float(r.total_hectares),
        )
        for r in rows
    ]


@router.get("/stats/avg-soil-moisture-by-village", response_model=list[AvgMoistureByVillage])
def avg_soil_moisture(
    hours: int = Query(1, ge=1, le=168),
    db: Session = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = (
        db.query(
            Village.name.label("village"),
            func.avg(SensorReading.soil_moisture_pct).label("avg_soil_moisture_pct"),
        )
        .join(Farmer, Farmer.village_id == Village.id)
        .join(Farm, Farm.farmer_id == Farmer.id)
        .join(SensorReading, SensorReading.farm_id == Farm.id)
        .filter(SensorReading.reading_time >= cutoff)
        .group_by(Village.name)
        .order_by(Village.name)
        .all()
    )
    return [
        AvgMoistureByVillage(
            village=r.village,
            avg_soil_moisture_pct=round(float(r.avg_soil_moisture_pct), 1),
        )
        for r in rows
    ]
