from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from typing import List

class CropBase(BaseModel):
    name: str
    variety: Optional[str] = None

class CropCreate(CropBase):
    pass

class CropUpdate(CropBase):
    id: str

class CropRead(CropBase):
    id: UUID

    model_config = {"from_attributes": True}

class CropList(BaseModel):
    crops: List[CropRead]

class InitialBiodataBase(BaseModel):
    farmer_id: UUID
    crop_id: UUID
    average_yield_kg: Optional[float] = None
    last_harvest_date: Optional[datetime] = None

class InitialBiodataCreate(InitialBiodataBase):
    pass

class InitialBiodataUpdate(BaseModel):
    id: str
    average_yield_kg: Optional[float] = None
    last_harvest_date: Optional[datetime] = None

class InitialBiodataRead(InitialBiodataBase):
    id: UUID
    model_config = {"from_attributes": True}

class InitialBiodataList(BaseModel):
    biodata: List[InitialBiodataRead]