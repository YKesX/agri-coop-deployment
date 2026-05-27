from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db: str
    version: str


class VillageOut(BaseModel):
    id: int
    name: str
    farmer_count: int = 0

    model_config = {"from_attributes": True}


class CropOut(BaseModel):
    id: int
    name: str
    current_price_usd_per_kg: float
    price_updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PriceOut(BaseModel):
    crop: str
    price_usd_per_kg: float


class FarmBrief(BaseModel):
    id: int
    crop_name: str
    area_hectares: float
    expected_yield_kg: float

    model_config = {"from_attributes": True}


class FarmerOut(BaseModel):
    id: str
    name: str
    village: Optional[str] = None
    joined_date: Optional[date] = None

    model_config = {"from_attributes": True}


class FarmerDetail(BaseModel):
    id: str
    name: str
    village: Optional[str] = None
    joined_date: Optional[date] = None
    farms: list[FarmBrief] = []

    model_config = {"from_attributes": True}


class SensorReadingOut(BaseModel):
    id: int
    farm_id: int
    reading_time: datetime
    temperature_c: float
    humidity_pct: float
    soil_moisture_pct: float

    model_config = {"from_attributes": True}


class SensorLatestOut(BaseModel):
    farm_id: int
    farmer_name: str
    reading_time: datetime
    temperature_c: float
    humidity_pct: float
    soil_moisture_pct: float

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    type: str
    severity: str
    message: str
    farm_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class YieldByVillage(BaseModel):
    village: str
    total_yield_kg: float
    total_hectares: float


class AvgMoistureByVillage(BaseModel):
    village: str
    avg_soil_moisture_pct: float
