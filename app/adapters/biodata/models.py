from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel


class Crop(BaseModel):
    __tablename__ = "crops"
    
    name = Column(String(50), nullable=False)  
    variety = Column(String(50))

    initial_records = relationship("InitialBiodata", back_populates="crop")

class InitialBiodata(BaseModel):
    __tablename__ = "initial_biodata"
    
    farmer_id = Column(PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_id = Column(PG_UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    
    average_yield_kg = Column(Numeric(10, 2))
    last_harvest_date = Column(DateTime)
    
    farmer = relationship("Farmer", back_populates="initial_biodata")
    crop = relationship("Crop", back_populates="initial_records")
