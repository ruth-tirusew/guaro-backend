from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class CropBase(BaseModel):
    name: str
    variety: Optional[str] = None

class CropCreate(CropBase):
    pass

class CropUpdate(CropBase):
    pass

class CropRead(CropBase):
    id: UUID

    model_config = {"from_attributes": True}

class InitialBiodataBase(BaseModel):
    farmer_id: UUID
    crop_id: UUID
    average_yield_kg: Optional[float] = None
    last_harvest_date: Optional[datetime] = None

class InitialBiodataCreate(InitialBiodataBase):
    pass

class InitialBiodataUpdate(BaseModel):
    average_yield_kg: Optional[float] = None
    last_harvest_date: Optional[datetime] = None

class InitialBiodataRead(InitialBiodataBase):
    id: UUID
    model_config = {"from_attributes": True}
