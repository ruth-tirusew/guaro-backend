from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class CropBase(BaseModel):
    name: str
    variety: Optional[str] = None
    price: Optional[float] = None
    initial_amount: Optional[float]=0.0
    harvest_season: str
    locality: str
    alternative_locality: Optional[str]=None
    accessible_resources: Optional[str]=None

class GoodsReceivingRead(BaseModel):
    id: UUID
    batch_number: str
    quantity: float
    transaction_date: datetime
    notes: Optional[str] = None
    crop_id: UUID
    warehouse_id: UUID
    farmer_id: UUID
    
    model_config = {"from_attributes": True}
    

class CropCreate(CropBase):
    pass

class CropUpdate(CropBase):
    id: UUID

class CropRead(CropBase):
    id: UUID
    receiving_transactions: List[GoodsReceivingRead] = [] 

    total_available: Optional[float] = None
    model_config = {"from_attributes": True}

class CropList(BaseModel):
    crops: List[CropRead]

class GRNRequest(BaseModel):
    warehouse_id: UUID
    crop_id: UUID
    farmer_id:UUID
    amount: float
    notes: Optional[str]=None

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