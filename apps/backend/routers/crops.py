from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import Crop
from schemas import CropOut, PriceOut

router = APIRouter()


@router.get("/crops", response_model=list[CropOut])
def list_crops(db: Session = Depends(get_db)):
    return db.query(Crop).order_by(Crop.name).all()


@router.get("/prices", response_model=list[PriceOut])
def list_prices(db: Session = Depends(get_db)):
    crops = db.query(Crop).order_by(Crop.name).all()
    return [
        PriceOut(crop=c.name, price_usd_per_kg=float(c.current_price_usd_per_kg))
        for c in crops
    ]
