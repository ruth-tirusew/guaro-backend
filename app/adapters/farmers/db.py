from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid
from typing import List, Optional
from datetime import datetime

from app.adapters.farmers.interface import IFarmerRepository
from app.adapters.farmers.models import Farmer, Address, LegalDocument, Gender, VerificationStatus

class FarmerRepository(IFarmerRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    # ====================== FARMER OPERATIONS ======================
    def create_farmer(self, farmer_data: dict) -> Farmer:
        try:
            farmer = Farmer(**farmer_data)
            self.db.add(farmer)
            self.db.commit()
            self.db.refresh(farmer)
            return farmer
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Farmer creation failed - duplicate phone number or address"
            )

    def get_farmer_by_id(self, farmer_id: str) -> Optional[Farmer]:
        return self.db.query(Farmer).filter(Farmer.id == farmer_id).first()

    def get_farmer_by_phone(self, phone_number: str) -> Optional[Farmer]:
        return self.db.query(Farmer).filter(Farmer.phone_number == phone_number).first()

    def get_all_farmers(self) -> List[Farmer]:
        return self.db.query(Farmer).all()

    def get_farmers_by_agent(self, agent_id: str) -> List[Farmer]:
        agent_uuid = uuid.UUID(agent_id)
        return self.db.query(Farmer).filter(Farmer.assigned_agent_id == agent_uuid).all()

    def update_farmer(self, farmer_id: str, update_data: dict) -> Optional[Farmer]:
        farmer = self.get_farmer_by_id(farmer_id)
        if not farmer:
            return None
        
        try:
            for key, value in update_data.items():
                if hasattr(farmer, key):
                    setattr(farmer, key, value)
            self.db.commit()
            self.db.refresh(farmer)
            return farmer
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Farmer update failed - duplicate phone number or address"
            )
    
    def activate_farmer(self, farmer_id: str) -> bool:
        farmer = self.get_farmer_by_id(farmer_id)
        if farmer:
            farmer.is_active = True
            self.db.commit()
            return True
        return False


    def deactivate_farmer(self, farmer_id: str) -> bool:
        farmer = self.get_farmer_by_id(farmer_id)
        if farmer:
            farmer.is_active = False
            self.db.commit()
            return True
        return False

    def delete_farmer(self, farmer_id: str) -> bool:
        farmer = self.get_farmer_by_id(farmer_id)
        if farmer:
            farmer.is_deleted = True
            self.db.commit()
            return True
        return False

    # ====================== ADDRESS OPERATIONS ======================
    def create_address(self, address_data: dict) -> Address:
        try:
            address = Address(**address_data)
            self.db.add(address)
            self.db.commit()
            self.db.refresh(address)
            return address
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Address creation failed"
            )

    def get_address_by_id(self, address_id: str) -> Optional[Address]:
        return self.db.query(Address).filter(Address.id == address_id).first()

    def get_address_by_farmer(self, farmer_id: str) -> Optional[Address]:
        farmer_uuid = uuid.UUID(farmer_id)
        farmer = self.db.query(Farmer).filter(Farmer.id == farmer_uuid).first()
        if farmer and farmer.address_id:
            return self.get_address_by_id(str(farmer.address_id))
        return None

    def update_address(self, address_id: str, update_data: dict) -> Optional[Address]:
        address = self.get_address_by_id(address_id)
        if not address:
            return None
        
        try:
            for key, value in update_data.items():
                if hasattr(address, key):
                    setattr(address, key, value)
            self.db.commit()
            self.db.refresh(address)
            return address
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Address update failed"
            )

    def delete_address(self, address_id: str) -> bool:
        address = self.get_address_by_id(address_id)
        if address:
            self.db.delete(address)
            self.db.commit()
            return True
        return False

    # ====================== LEGAL DOCUMENT OPERATIONS ======================
    def create_legal_document(self, document_data: dict) -> LegalDocument:
        try:
            document = LegalDocument(**document_data)
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            return document
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Legal document creation failed"
            )

    def get_legal_document_by_id(self, document_id: str) -> Optional[LegalDocument]:
        uuid_obj = uuid.UUID(document_id)
        return self.db.query(LegalDocument).filter(LegalDocument.id == uuid_obj).first()

    def get_legal_documents_by_farmer(self, farmer_id: str) -> List[LegalDocument]:
        return self.db.query(LegalDocument).filter(LegalDocument.farmer_id == farmer_id).all()

    def get_legal_documents_by_type(self, farmer_id: str, document_type: str) -> List[LegalDocument]:
        farmer_uuid = uuid.UUID(farmer_id)
        return self.db.query(LegalDocument).filter(
            LegalDocument.farmer_id == farmer_uuid,
            LegalDocument.document_type == document_type
        ).all()

    def update_legal_document(self, document_id: str, update_data: dict) -> Optional[LegalDocument]:
        document = self.get_legal_document_by_id(document_id)
        if not document:
            return None
        
        try:
            for key, value in update_data.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            self.db.commit()
            self.db.refresh(document)
            return document
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Legal document update failed"
            )

    def delete_legal_document(self, document_id: str) -> bool:
        document = self.get_legal_document_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False

    # ====================== RELATIONSHIP OPERATIONS ======================
    def assign_farmer_to_agent(self, farmer_id: str, agent_id: str) -> bool:
        farmer = self.get_farmer_by_id(farmer_id)
        if farmer:
            farmer.assigned_agent_id = uuid.UUID(agent_id)
            self.db.commit()
            return True
        return False

    def unassign_farmer_from_agent(self, farmer_id: str) -> bool:
        farmer = self.get_farmer_by_id(farmer_id)
        if farmer:
            farmer.assigned_agent_id = None
            self.db.commit()
            return True
        return False

    def get_farmer_with_relationships(self, farmer_id: str) -> Optional[Farmer]:
        uuid_obj = uuid.UUID(farmer_id)
        return self.db.query(Farmer).options(
        
        ).filter(Farmer.id == uuid_obj).first()

    # ====================== SEARCH AND FILTER OPERATIONS ======================
    def search_farmers_by_name(self, name: str) -> List[Farmer]:
        return self.db.query(Farmer).filter(
            Farmer.full_name.ilike(f"%{name}%")
        ).all()

    def get_farmers_by_registration_date_range(self, start_date: datetime, end_date: datetime) -> List[Farmer]:
        return self.db.query(Farmer).filter(
            Farmer.registration_date >= start_date,
            Farmer.registration_date <= end_date
        ).all()

    def get_farmers_by_educational_background(self, education: str) -> List[Farmer]:
        return self.db.query(Farmer).filter(
            Farmer.educational_background.ilike(f"%{education}%")
        ).all()