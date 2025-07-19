from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from app.adapters.farmers.interface import IFarmerRepository
from app.adapters.farmers.models import Farmer, Address, LegalDocument, Gender, VerificationStatus

class MockFarmerRepository(IFarmerRepository):
    def __init__(self):
        self.farmers = {}
        self.addresses = {}
        self.legal_documents = {}

    # ====================== FARMER OPERATIONS ======================
    def create_farmer(self, farmer_data: dict) -> Farmer:
        farmer_id = str(uuid4())
        farmer = Farmer(
            id=farmer_id,
            full_name=farmer_data.get('full_name'),
            gender=farmer_data.get('gender'),
            educational_background=farmer_data.get('educational_background'),
            phone_number=farmer_data.get('phone_number'),
            address_id=farmer_data.get('address_id'),
            assigned_agent_id=farmer_data.get('assigned_agent_id'),
            registration_date=farmer_data.get('registration_date', datetime.utcnow()),
            is_active=farmer_data.get('is_active', True)
        )
        self.farmers[farmer_id] = farmer
        return farmer

    def get_farmer_by_id(self, farmer_id: str) -> Optional[Farmer]:
        return self.farmers.get(farmer_id)

    def get_farmer_by_phone(self, phone_number: str) -> Optional[Farmer]:
        for farmer in self.farmers.values():
            if farmer.phone_number == phone_number:
                return farmer
        return None

    def get_all_farmers(self) -> List[Farmer]:
        return list(self.farmers.values())

    def get_farmers_by_agent(self, agent_id: str) -> List[Farmer]:
        return [farmer for farmer in self.farmers.values() if farmer.assigned_agent_id == agent_id]

    def update_farmer(self, farmer_id: str, update_data: dict) -> Optional[Farmer]:
        if farmer_id not in self.farmers:
            return None
        farmer = self.farmers[farmer_id]
        for key, value in update_data.items():
            if hasattr(farmer, key):
                setattr(farmer, key, value)
        return farmer

    def delete_farmer(self, farmer_id: str) -> bool:
        if farmer_id in self.farmers:
            del self.farmers[farmer_id]
            return True
        return False

    def deactivate_farmer(self, farmer_id: str) -> bool:
        if farmer_id in self.farmers:
            self.farmers[farmer_id].is_active = False
            return True
        return False

    def activate_farmer(self, farmer_id: str) -> bool:
        if farmer_id in self.farmers:
            self.farmers[farmer_id].is_active = True
            return True
        return False

    # ====================== ADDRESS OPERATIONS ======================
    def create_address(self, address_data: dict) -> Address:
        address_id = str(uuid4())
        address = Address(
            id=address_id,
            zone_or_sub_city=address_data.get('zone_or_sub_city'),
            kebele=address_data.get('kebele'),
            woreda=address_data.get('woreda')
        )
        self.addresses[address_id] = address
        return address

    def get_address_by_id(self, address_id: str) -> Optional[Address]:
        return self.addresses.get(address_id)

    def get_address_by_farmer(self, farmer_id: str) -> Optional[Address]:
        farmer = self.farmers.get(farmer_id)
        if farmer and farmer.address_id:
            return self.addresses.get(str(farmer.address_id))
        return None

    def update_address(self, address_id: str, update_data: dict) -> Optional[Address]:
        if address_id not in self.addresses:
            return None
        address = self.addresses[address_id]
        for key, value in update_data.items():
            if hasattr(address, key):
                setattr(address, key, value)
        return address

    def delete_address(self, address_id: str) -> bool:
        if address_id in self.addresses:
            del self.addresses[address_id]
            return True
        return False

    # ====================== LEGAL DOCUMENT OPERATIONS ======================
    def create_legal_document(self, document_data: dict) -> LegalDocument:
        document_id = str(uuid4())
        document = LegalDocument(
            id=document_id,
            farmer_id=document_data.get('farmer_id'),
            document_type=document_data.get('document_type'),
            document_url=document_data.get('document_url'),
            issue_date=document_data.get('issue_date')
        )
        self.legal_documents[document_id] = document
        return document

    def get_legal_document_by_id(self, document_id: str) -> Optional[LegalDocument]:
        return self.legal_documents.get(document_id)

    def get_legal_documents_by_farmer(self, farmer_id: str) -> List[LegalDocument]:
        return [doc for doc in self.legal_documents.values() if doc.farmer_id == farmer_id]

    def get_legal_documents_by_type(self, farmer_id: str, document_type: str) -> List[LegalDocument]:
        return [doc for doc in self.legal_documents.values() 
                if doc.farmer_id == farmer_id and doc.document_type == document_type]

    def update_legal_document(self, document_id: str, update_data: dict) -> Optional[LegalDocument]:
        if document_id not in self.legal_documents:
            return None
        document = self.legal_documents[document_id]
        for key, value in update_data.items():
            if hasattr(document, key):
                setattr(document, key, value)
        return document

    def delete_legal_document(self, document_id: str) -> bool:
        if document_id in self.legal_documents:
            del self.legal_documents[document_id]
            return True
        return False

    # ====================== RELATIONSHIP OPERATIONS ======================
    def assign_farmer_to_agent(self, farmer_id: str, agent_id: str) -> bool:
        if farmer_id in self.farmers:
            self.farmers[farmer_id].assigned_agent_id = agent_id
            return True
        return False

    def unassign_farmer_from_agent(self, farmer_id: str) -> bool:
        if farmer_id in self.farmers:
            self.farmers[farmer_id].assigned_agent_id = None
            return True
        return False

    def get_farmer_with_relationships(self, farmer_id: str) -> Optional[Farmer]:
        farmer = self.farmers.get(farmer_id)
        if not farmer:
            return None

        # Attach address
        if hasattr(farmer, "address_id") and farmer.address_id:
            farmer.address = self.addresses.get(farmer.address_id)
        else:
            farmer.address = None

        # Attach legal documents
        farmer.legal_documents = [
            doc for doc in self.legal_documents.values() if doc.farmer_id == farmer_id
        ]

        # Attach assigned agent (if present)
        if hasattr(farmer, "assigned_agent_id") and farmer.assigned_agent_id:
            farmer.assigned_agent = self.agents.get(farmer.assigned_agent_id)
        else:
            farmer.assigned_agent = None

        # Attach initial biodata (if present)
        if hasattr(self, "initial_biodata"):
            farmer.initial_biodata = [
                bio for bio in self.initial_biodata.values() if bio.farmer_id == farmer_id
            ]
        else:
            farmer.initial_biodata = []

        return farmer

    # ====================== SEARCH AND FILTER OPERATIONS ======================
    def search_farmers_by_name(self, name: str) -> List[Farmer]:
        name_lower = name.lower()
        return [farmer for farmer in self.farmers.values() 
                if name_lower in farmer.full_name.lower()]

    def get_farmers_by_registration_date_range(self, start_date: datetime, end_date: datetime) -> List[Farmer]:
        return [farmer for farmer in self.farmers.values() 
                if start_date <= farmer.registration_date <= end_date]

    def get_farmers_by_educational_background(self, education: str) -> List[Farmer]:
        education_lower = education.lower()
        return [farmer for farmer in self.farmers.values() 
                if farmer.educational_background and education_lower in farmer.educational_background.lower()]
