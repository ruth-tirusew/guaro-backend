from datetime import datetime, timezone
from enum import Enum as PyEnum
from uuid import uuid4, UUID
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Boolean, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


# ====================== CORE ENUMS ======================
class Gender(str, PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class VerificationStatus(str, PyEnum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"


# ====================== LOCATION MODELS ======================
class Address(BaseModel):
    __tablename__ = "addresses"
    
    zone_or_sub_city = Column(String(100), nullable=False)
    kebele = Column(String(100), nullable=False)
    woreda = Column(String(100), nullable=False)
    
    farmer = relationship("Farmer", back_populates="address", uselist=False)


class Farmer(BaseModel):
    __tablename__ = "farmers"
    
    full_name = Column(String(100), nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    educational_background = Column(String(255), nullable=True)
    phone_number = Column(String(20), unique=True)
    address_id = Column(PG_UUID(as_uuid=True), ForeignKey("addresses.id"), unique=True)
    registration_date = Column(DateTime, default=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    address = relationship("Address", back_populates="farmer")
    legal_documents = relationship("LegalDocument", back_populates="farmer", 
                                 cascade="all, delete-orphan")
    initial_biodata = relationship("InitialBiodata", back_populates="farmer",
                                 cascade="all, delete-orphan")
   

class FarmerContracts(BaseModel):
    __tablename__="farmer_contracts"
    
    farmer_id = Column(PG_UUID(as_uuid=True), ForeignKey("farmers.id"))
    contract_name = Column(String(100), nullable=False)
    document_url = Column(String(100), nullable=False)




class LegalDocument(BaseModel):
    __tablename__ = "legal_documents"
    
    farmer_id = Column(PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    document_type = Column(String(50), nullable=False)
    document_url = Column(String(255))
    issue_date = Column(DateTime)
    
    farmer = relationship("Farmer", back_populates="legal_documents")
