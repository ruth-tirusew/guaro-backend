import uuid
from datetime import datetime
from typing import List, Optional

from app.adapters.farmers.interface import IFarmerRepository
from app.modules.farmers.schemas import (
    FarmerCreate, FarmerUpdate, FarmerRead, FarmerList,
    AddressCreate, AddressUpdate, AddressRead, AddressList,
    LegalDocumentCreate, LegalDocumentUpdate, LegalDocumentRead, LegalDocumentList,
    FarmerDetailResponse
)

class FarmerService:
    def __init__(self, farmer_repository: IFarmerRepository):
        self.repository = farmer_repository

    # ====================== FARMER OPERATIONS ======================
    def create_farmer(self, farmer_data: FarmerCreate) -> FarmerRead:
        """Create a farmer with address and legal documents"""
        existing_farmer = self.repository.get_farmer_by_phone(farmer_data.phone_number)
        if existing_farmer:
            raise ValueError("A farmer with this phone number already exists")

        address_data = {
            'zone_or_sub_city': farmer_data.address.zone_or_sub_city,
            'kebele': farmer_data.address.kebele,
            'woreda': farmer_data.address.woreda
        }
        address = self.repository.create_address(address_data)

        farmer_data_dict = {
            'full_name': farmer_data.full_name,
            'gender': farmer_data.gender,
            'educational_background': farmer_data.educational_background,
            'phone_number': farmer_data.phone_number,
            'address_id': address.id,
            'registration_date': datetime.utcnow(),
            'is_active': True
        }
        farmer = self.repository.create_farmer(farmer_data_dict)

        legal_documents = []
        if farmer_data.legal_documents:
            for doc_data in farmer_data.legal_documents:
                document_data = {
                    'farmer_id': farmer.id,
                    'document_type': doc_data.document_type,
                    'document_url': doc_data.document_url,
                    'issue_date': doc_data.issue_date
                }
                document = self.repository.create_legal_document(document_data)
                legal_documents.append(document)

        return self._convert_farmer_to_read(farmer, address, legal_documents)

    def get_farmer(self, farmer_id: str) -> Optional[FarmerRead]:
        """Get a farmer by ID with relationships"""
        farmer = self.repository.get_farmer_by_id(farmer_id)
        if not farmer:
            return None

        address = None
        legal_documents = []
        
        if farmer.address_id:
            address = self.repository.get_address_by_id(str(farmer.address_id))
        
        legal_documents = self.repository.get_legal_documents_by_farmer(farmer_id)

        return self._convert_farmer_to_read(farmer, address, legal_documents)

    def get_farmer_by_phone(self, phone_number: str) -> Optional[FarmerRead]:
        """Get a farmer by phone number"""
        farmer = self.repository.get_farmer_by_phone(phone_number)
        if not farmer:
            return None

        address = None
        legal_documents = []
        
        if farmer.address_id:
            address = self.repository.get_address_by_id(str(farmer.address_id))
        
        legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))

        return self._convert_farmer_to_read(farmer, address, legal_documents)

    def list_farmers(self) -> FarmerList:
        """Get all farmers"""
        farmers = self.repository.get_all_farmers()
        farmer_reads = []
        
        for farmer in farmers:
            address = None
            legal_documents = []
            
            if farmer.address_id:
                address = self.repository.get_address_by_id(str(farmer.address_id))
            
            legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))
            
            farmer_read = self._convert_farmer_to_read(farmer, address, legal_documents)
            farmer_reads.append(farmer_read)

        return FarmerList(farmers=farmer_reads)

    def get_farmers_by_agent(self, agent_id: str) -> List[FarmerRead]:
        """Get all farmers assigned to a specific agent"""
        farmers = self.repository.get_farmers_by_agent(agent_id)
        farmer_reads = []
        
        for farmer in farmers:
            address = None
            legal_documents = []
            
            if farmer.address_id:
                address = self.repository.get_address_by_id(str(farmer.address_id))
            
            legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))
            
            farmer_read = self._convert_farmer_to_read(farmer, address, legal_documents)
            farmer_reads.append(farmer_read)

        return farmer_reads

    def update_farmer(self, farmer_id: str, update_data: FarmerUpdate) -> Optional[FarmerRead]:
        """
        Update a farmer and related data (address, legal documents).
        This is a real implementation.
        """
        # Fetch the farmer
        farmer = self.repository.get_farmer_by_id(farmer_id)
        if not farmer:
            return None

        # Check for phone number uniqueness if changed
        if update_data.phone_number and update_data.phone_number != farmer.phone_number:
            existing_farmer = self.repository.get_farmer_by_phone(update_data.phone_number)
            if existing_farmer and str(existing_farmer.id) != str(farmer_id):
                raise ValueError("A farmer with this phone number already exists")

        # Prepare update dict for farmer fields
        farmer_update_dict = {}
        if update_data.full_name is not None:
            farmer_update_dict['full_name'] = update_data.full_name
        if update_data.gender is not None:
            farmer_update_dict['gender'] = update_data.gender
        if update_data.educational_background is not None:
            farmer_update_dict['educational_background'] = update_data.educational_background
        if update_data.phone_number is not None:
            farmer_update_dict['phone_number'] = update_data.phone_number

        # Update farmer if there are changes
        if farmer_update_dict:
            farmer = self.repository.update_farmer(farmer_id, farmer_update_dict)

        address = None
        if update_data.address and farmer.address_id:
            address_update_dict = {}
            if update_data.address.zone_or_sub_city is not None:
                address_update_dict['zone_or_sub_city'] = update_data.address.zone_or_sub_city
            if update_data.address.kebele is not None:
                address_update_dict['kebele'] = update_data.address.kebele
            if update_data.address.woreda is not None:
                address_update_dict['woreda'] = update_data.address.woreda

            if address_update_dict:
                address = self.repository.update_address(str(farmer.address_id), address_update_dict)
            else:
                address = self.repository.get_address_by_id(str(farmer.address_id))
        elif farmer.address_id:
            address = self.repository.get_address_by_id(str(farmer.address_id))

        legal_documents = []
        if update_data.legal_documents is not None:
            # Remove all existing legal documents for this farmer
            existing_docs = self.repository.get_legal_documents_by_farmer(farmer_id)
            for doc in existing_docs:
                self.repository.delete_legal_document(str(doc.id))
            # Add new legal documents
            for doc_data in update_data.legal_documents:
                document_data = {
                    'farmer_id': farmer_id,
                    'document_type': doc_data.document_type,
                    'document_url': doc_data.document_url,
                    'issue_date': doc_data.issue_date
                }
                document = self.repository.create_legal_document(document_data)
                legal_documents.append(document)
        else:
            legal_documents = self.repository.get_legal_documents_by_farmer(farmer_id)

        return self._convert_farmer_to_read(farmer, address, legal_documents)

    def delete_farmer(self, farmer_id: str) -> bool:
        """Delete a farmer and all related data"""
        farmer = self.repository.get_farmer_by_id(farmer_id)
        if not farmer:
            return False

        legal_documents = self.repository.get_legal_documents_by_farmer(farmer_id)
        for doc in legal_documents:
            self.repository.delete_legal_document(str(doc.id))

        if farmer.address_id:
            self.repository.delete_address(str(farmer.address_id))

        return self.repository.delete_farmer(farmer_id)

    def deactivate_farmer(self, farmer_id: str) -> bool:
        """Deactivate a farmer"""
        return self.repository.deactivate_farmer(farmer_id)

    def activate_farmer(self, farmer_id: str) -> bool:
        """Activate a farmer"""
        return self.repository.activate_farmer(farmer_id)

    # ====================== ADDRESS OPERATIONS ======================
    def create_address(self, address_data: AddressCreate) -> AddressRead:
        """Create a new address"""
        address_dict = {
            'zone_or_sub_city': address_data.zone_or_sub_city,
            'kebele': address_data.kebele,
            'woreda': address_data.woreda
        }
        address = self.repository.create_address(address_dict)
        return self._convert_address_to_read(address)

    def get_address(self, address_id: str) -> Optional[AddressRead]:
        """Get an address by ID"""
        address = self.repository.get_address_by_id(address_id)
        return self._convert_address_to_read(address) if address else None

    def update_address(self, address_id: str, update_data: AddressUpdate) -> Optional[AddressRead]:
        """Update an address"""
        address_update_dict = {}
        if update_data.zone_or_sub_city is not None:
            address_update_dict['zone_or_sub_city'] = update_data.zone_or_sub_city
        if update_data.kebele is not None:
            address_update_dict['kebele'] = update_data.kebele
        if update_data.woreda is not None:
            address_update_dict['woreda'] = update_data.woreda

        address = self.repository.update_address(address_id, address_update_dict)
        return self._convert_address_to_read(address) if address else None

    def delete_address(self, address_id: str) -> bool:
        """Delete an address"""
        return self.repository.delete_address(address_id)

    # ====================== LEGAL DOCUMENT OPERATIONS ======================
    def create_legal_document(self, document_data: LegalDocumentCreate) -> LegalDocumentRead:
        """Create a new legal document"""
        document_dict = {
            'farmer_id': document_data.farmer_id,
            'document_type': document_data.document_type,
            'document_url': document_data.document_url,
            'issue_date': document_data.issue_date
        }
        document = self.repository.create_legal_document(document_dict)
        return self._convert_legal_document_to_read(document)

    def get_legal_document(self, document_id: str) -> Optional[LegalDocumentRead]:
        """Get a legal document by ID"""
        document = self.repository.get_legal_document_by_id(document_id)
        return self._convert_legal_document_to_read(document) if document else None

    def get_legal_documents_by_farmer(self, farmer_id: str) -> LegalDocumentList:
        """Get all legal documents for a farmer"""
        documents = self.repository.get_legal_documents_by_farmer(farmer_id)
        document_reads = [self._convert_legal_document_to_read(doc) for doc in documents]
        return LegalDocumentList(legal_documents=document_reads)

    def update_legal_document(self, document_id: str, update_data: LegalDocumentUpdate) -> Optional[LegalDocumentRead]:
        """Update a legal document"""
        document_update_dict = {}
        if update_data.document_type is not None:
            document_update_dict['document_type'] = update_data.document_type
        if update_data.document_url is not None:
            document_update_dict['document_url'] = update_data.document_url
        if update_data.issue_date is not None:
            document_update_dict['issue_date'] = update_data.issue_date

        document = self.repository.update_legal_document(document_id, document_update_dict)
        return self._convert_legal_document_to_read(document) if document else None

    def delete_legal_document(self, document_id: str) -> bool:
        """Delete a legal document"""
        return self.repository.delete_legal_document(document_id)

    # ====================== RELATIONSHIP OPERATIONS ======================
    def assign_farmer_to_agent(self, farmer_id: str, agent_id: str) -> bool:
        """Assign a farmer to an agent"""
        return self.repository.assign_farmer_to_agent(farmer_id, agent_id)

    def unassign_farmer_from_agent(self, farmer_id: str) -> bool:
        """Unassign a farmer from their current agent"""
        return self.repository.unassign_farmer_from_agent(farmer_id)

    # ====================== SEARCH AND FILTER OPERATIONS ======================
    def search_farmers_by_name(self, name: str) -> FarmerList:
        """Search farmers by name"""
        farmers = self.repository.search_farmers_by_name(name)
        farmer_reads = []
        
        for farmer in farmers:
            address = None
            legal_documents = []
            
            if farmer.address_id:
                address = self.repository.get_address_by_id(str(farmer.address_id))
            
            legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))
            
            farmer_read = self._convert_farmer_to_read(farmer, address, legal_documents)
            farmer_reads.append(farmer_read)

        return FarmerList(farmers=farmer_reads)

    def get_farmers_by_registration_date_range(self, start_date: datetime, end_date: datetime) -> FarmerList:
        """Get farmers registered within a date range"""
        farmers = self.repository.get_farmers_by_registration_date_range(start_date, end_date)
        farmer_reads = []
        
        for farmer in farmers:
            address = None
            legal_documents = []
            
            if farmer.address_id:
                address = self.repository.get_address_by_id(str(farmer.address_id))
            
            legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))
            
            farmer_read = self._convert_farmer_to_read(farmer, address, legal_documents)
            farmer_reads.append(farmer_read)

        return FarmerList(farmers=farmer_reads)

    def get_farmers_by_educational_background(self, education: str) -> FarmerList:
        """Get farmers by educational background"""
        farmers = self.repository.get_farmers_by_educational_background(education)
        farmer_reads = []
        
        for farmer in farmers:
            address = None
            legal_documents = []
            
            if farmer.address_id:
                address = self.repository.get_address_by_id(str(farmer.address_id))
            
            legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))
            
            farmer_read = self._convert_farmer_to_read(farmer, address, legal_documents)
            farmer_reads.append(farmer_read)

        return FarmerList(farmers=farmer_reads)

    # ====================== HELPER METHODS ======================
    def _convert_farmer_to_read(self, farmer, address=None, legal_documents=None) -> FarmerRead:
        """Convert farmer model to read schema"""
        address_read = None
        if address:
            address_read = self._convert_address_to_read(address)

        legal_document_reads = []
        if legal_documents:
            legal_document_reads = [self._convert_legal_document_to_read(doc) for doc in legal_documents]

        return FarmerRead(
            id=str(farmer.id),
            full_name=farmer.full_name,
            gender=farmer.gender,
            educational_background=farmer.educational_background,
            phone_number=farmer.phone_number,
            address_id=str(farmer.address_id) if farmer.address_id else None,
            registration_date=farmer.registration_date,
            is_active=farmer.is_active,
            address=address_read,
            legal_documents=legal_document_reads
        )

    def _convert_address_to_read(self, address) -> AddressRead:
        """Convert address model to read schema"""
        return AddressRead(
            id=str(address.id),
            zone_or_sub_city=address.zone_or_sub_city,
            kebele=address.kebele,
            woreda=address.woreda
        )

    def _convert_legal_document_to_read(self, document) -> LegalDocumentRead:
        """Convert legal document model to read schema"""
        return LegalDocumentRead(
            id=str(document.id),
            farmer_id=str(document.farmer_id),
            document_type=document.document_type,
            document_url=document.document_url,
            issue_date=document.issue_date
        )

