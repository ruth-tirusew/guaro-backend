import uuid
import re
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator,Field
from typing import Optional, List

from app.adapters.farmers.models import Gender, VerificationStatus

# ====================== VALIDATION PATTERNS ======================
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")

# ====================== ADDRESS SCHEMAS ======================
class AddressBase(BaseModel):
    zone_or_sub_city: str
    kebele: str
    woreda: str

    @field_validator("zone_or_sub_city", "kebele", "woreda")
    @classmethod
    def validate_location_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Location field must not be empty")
        return v.strip()

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    zone_or_sub_city: Optional[str] = None
    kebele: Optional[str] = None
    woreda: Optional[str] = None


class AddressRead(AddressBase):
    id: uuid.UUID
    model_config = {"from_attributes": True}


# ====================== LEGAL DOCUMENT SCHEMAS ======================
class LegalDocumentBase(BaseModel):
    document_type: str
    document_url: str
    issue_date: Optional[datetime] = None

class LegalDocumentCreate(LegalDocumentBase):
    farmer_id: Optional[uuid.UUID]=None

class LegalDocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_url: Optional[str] = None
    issue_date: Optional[datetime] = None


class LegalDocumentRead(LegalDocumentBase):
    id: uuid.UUID
    farmer_id: str
    model_config = {"from_attributes": True}

# ====================== FARMER SCHEMAS ======================
class FarmerBase(BaseModel):
    full_name: str
    gender: Gender
    educational_background: Optional[str] = None
    phone_number: str = Field(pattern=PHONE_REGEX)

class FarmerCreate(FarmerBase):
    address: AddressCreate
    legal_documents: Optional[List[LegalDocumentCreate]] = []

class FarmerUpdate(BaseModel):
    id: uuid.UUID
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    educational_background: Optional[str] = None
    phone_number: Optional[str] = Field(pattern=PHONE_REGEX)
    address: Optional[AddressUpdate] = None
    legal_documents: Optional[List[LegalDocumentCreate]] = []


# ====================== RESPONSE SCHEMAS ======================

class FarmerRead(FarmerBase):
    id: uuid.UUID
    address_id: Optional[uuid.UUID] = None
    assigned_agent_id: Optional[uuid.UUID] = None
    registration_date: datetime
    is_active: bool
    address: Optional[AddressRead] = None
    legal_documents: List[LegalDocumentRead] = []
    model_config = {"from_attributes": True}

class FarmerList(BaseModel):
    farmers: List[FarmerRead]

class FarmerDetailResponse(BaseModel):
    farmer: FarmerRead
    address: Optional[AddressRead] = None
    legal_documents: List[LegalDocumentRead] = []

class AddressList(BaseModel):
    addresses: List[AddressRead]

class LegalDocumentList(BaseModel):
    legal_documents: List[LegalDocumentRead]
