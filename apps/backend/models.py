from sqlalchemy import (
    Column, Integer, BigInteger, Text, Numeric, Date, DateTime, ForeignKey, Index,
    func,
)
from sqlalchemy.orm import relationship
from db import Base


class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)

    farmers = relationship("Farmer", back_populates="village")


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    current_price_usd_per_kg = Column(Numeric(10, 2), nullable=False)
    price_updated_at = Column(DateTime(timezone=True), server_default=func.now())

    farms = relationship("Farm", back_populates="crop")


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    village_id = Column(Integer, ForeignKey("villages.id"))
    joined_date = Column(Date, server_default=func.current_date())

    village = relationship("Village", back_populates="farmers")
    farms = relationship("Farm", back_populates="farmer")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True)
    farmer_id = Column(Text, ForeignKey("farmers.id"))
    crop_id = Column(Integer, ForeignKey("crops.id"))
    area_hectares = Column(Numeric(8, 2))
    expected_yield_kg = Column(Numeric(12, 2))

    farmer = relationship("Farmer", back_populates="farms")
    crop = relationship("Crop", back_populates="farms")
    sensor_readings = relationship("SensorReading", back_populates="farm")
    alerts = relationship("Alert", back_populates="farm")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(BigInteger, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    reading_time = Column(DateTime(timezone=True), server_default=func.now())
    temperature_c = Column(Numeric(5, 2))
    humidity_pct = Column(Numeric(5, 2))
    soil_moisture_pct = Column(Numeric(5, 2))

    farm = relationship("Farm", back_populates="sensor_readings")

    __table_args__ = (
        Index("idx_sensor_readings_farm_time", "farm_id", reading_time.desc()),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)
    severity = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    farm = relationship("Farm", back_populates="alerts")
