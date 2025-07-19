import uuid
import re
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator
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

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [self.zone_or_sub_city, self.kebele, self.woreda]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self

class AddressRead(AddressBase):
    id: str
    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

# ====================== LEGAL DOCUMENT SCHEMAS ======================
class LegalDocumentBase(BaseModel):
    document_type: str
    document_url: Optional[str] = None
    issue_date: Optional[datetime] = None

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        if not v or not v.strip():
            raise ValueError("Document type must not be empty")
        return v.strip()

class LegalDocumentCreate(LegalDocumentBase):
    farmer_id: str

    @field_validator("farmer_id")
    @classmethod
    def validate_farmer_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid farmer ID format")

class LegalDocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_url: Optional[str] = None
    issue_date: Optional[datetime] = None

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [self.document_type, self.document_url, self.issue_date]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self

class LegalDocumentRead(LegalDocumentBase):
    id: str
    farmer_id: str
    model_config = {"from_attributes": True}

    @field_validator("id", "farmer_id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

# ====================== FARMER SCHEMAS ======================
class FarmerBase(BaseModel):
    full_name: str
    gender: Gender
    educational_background: Optional[str] = None
    phone_number: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Full name must not be empty")
        return v.strip()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Phone number must not be empty")
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone number format")
        return v.strip()

    @field_validator("educational_background")
    @classmethod
    def validate_educational_background(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None

class FarmerCreate(FarmerBase):
    address: AddressCreate
    legal_documents: Optional[List[LegalDocumentCreate]] = []

class FarmerUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    educational_background: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[AddressUpdate] = None
    legal_documents: Optional[List[LegalDocumentCreate]] = []


    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Full name must not be empty")
        return v.strip() if v else None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Phone number must not be empty")
            if not PHONE_REGEX.match(v):
                raise ValueError("Invalid phone number format")
            return v.strip()
        return v

    @field_validator("educational_background")
    @classmethod
    def validate_educational_background(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [self.full_name, self.gender, self.educational_background, 
                 self.phone_number, self.address]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self


# ====================== RESPONSE SCHEMAS ======================

class FarmerRead(FarmerBase):
    id: str
    address_id: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    registration_date: datetime
    is_active: bool
    address: Optional[AddressRead] = None
    legal_documents: List[LegalDocumentRead] = []
    model_config = {"from_attributes": True}

    @field_validator("id", "address_id", "assigned_agent_id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

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
