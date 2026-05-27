from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from db import get_db
from models import SensorReading, Farm, Farmer
from schemas import SensorReadingOut, SensorLatestOut

router = APIRouter()


@router.get("/sensors/{farm_id}/readings", response_model=list[SensorReadingOut])
def get_readings(
    farm_id: int,
    limit: int = Query(24, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.reading_time.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.get("/sensors/latest", response_model=list[SensorLatestOut])
def latest_readings(db: Session = Depends(get_db)):
    subq = (
        db.query(
            SensorReading.farm_id,
            func.max(SensorReading.id).label("max_id"),
        )
        .group_by(SensorReading.farm_id)
        .subquery()
    )
    rows = (
        db.query(SensorReading, Farmer.name.label("farmer_name"))
        .join(subq, SensorReading.id == subq.c.max_id)
        .join(Farm, Farm.id == SensorReading.farm_id)
        .join(Farmer, Farmer.id == Farm.farmer_id)
        .all()
    )
    return [
        SensorLatestOut(
            farm_id=r.SensorReading.farm_id,
            farmer_name=r.farmer_name,
            reading_time=r.SensorReading.reading_time,
            temperature_c=float(r.SensorReading.temperature_c),
            humidity_pct=float(r.SensorReading.humidity_pct),
            soil_moisture_pct=float(r.SensorReading.soil_moisture_pct),
        )
        for r in rows
    ]
