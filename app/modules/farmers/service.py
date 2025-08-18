import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.adapters.farmers.interface import IFarmerRepository
from app.core.exceptions import ErrorFactory
from app.logging import logging
from app.modules.farmers.schemas import (
    FarmerCreate, FarmerUpdate, FarmerRead, FarmerList,FarmerDetailResponse,
    AddressCreate, AddressUpdate, AddressRead, AddressList,
    LegalDocumentCreate, LegalDocumentUpdate, LegalDocumentRead, LegalDocumentList,
    FarmerContractCreate, FarmerContractUpdate
)

class FarmerService:
    def __init__(self, farmer_repository: IFarmerRepository):
        self.repository = farmer_repository

    # ====================== FARMER OPERATIONS ======================
    def create_farmer(self, farmer_data: FarmerCreate) -> FarmerRead:
        try:
            """Create a farmer with address and legal documents"""
            existing_farmer = self.repository.get_farmer_by_phone(farmer_data.phone_number)
            if existing_farmer:
                raise ValueError("A farmer with this phone number already exists")

            address = self.repository.create_address(farmer_data.address.model_dump())

            farmer_data_dict = {
                'full_name': farmer_data.full_name,
                'gender': farmer_data.gender,
                'educational_background': farmer_data.educational_background,
                'phone_number': farmer_data.phone_number,
                'address_id': address.id,
                'registration_date': datetime.now(timezone.utc),
                'is_active': True
            }
            farmer = self.repository.create_farmer(farmer_data_dict)

            legal_documents = []
            if farmer_data.legal_documents:
                for doc_data in farmer_data.legal_documents:
                    document = self.repository.create_legal_document(doc_data.model_dump())
                    legal_documents.append(document)

            if farmer_data.consent_form:
                consent_dict = farmer_data.consent_form.model_dump()
                consent_dict['document_url']=str(farmer_data.consent_form.document_url)
                consent_form =self.repository.add_farmer_contract(consent_dict)

            return self._convert_farmer_to_read(farmer, address, legal_documents)

        except ValueError as e:
            logging.error(f"Error while creating farmer {str(e)}")
            raise ErrorFactory.bad_request(
                message=str(e),
                context={
                    "farmer_service":"create_farmer"
                }
            )

    def get_farmer(self, farmer_id: uuid.UUID) -> Optional[FarmerRead]:
        """Get a farmer by ID with relationships"""
        farmer = self.repository.get_farmer_by_id(farmer_id)
        if not farmer:
            return None

        address = self._get_farmer_address(farmer)
        legal_documents = self.repository.get_legal_documents_by_farmer(farmer_id)

        return self._convert_farmer_to_read(farmer, address, legal_documents)

    def get_farmer_by_phone(self, phone_number: str) -> Optional[FarmerRead]:
        """Get a farmer by phone number"""
        farmer = self.repository.get_farmer_by_phone(phone_number)
        if not farmer:
            return None

        address = self._get_farmer_address(farmer)
        legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))

        return self._convert_farmer_to_read(farmer, address, legal_documents)

    def list_farmers(self) -> FarmerList:
        """Get all farmers"""
        farmers = self.repository.get_all_farmers()
        farmer_reads = [self._build_farmer_read(farmer) for farmer in farmers]
        return FarmerList(farmers=farmer_reads)

    def update_farmer(self, update_data: FarmerUpdate) -> Optional[FarmerRead]:
        try:
            farmer = self.repository.get_farmer_by_id(update_data.id)
            if not farmer:
                return None

            # Validate phone number uniqueness if changed
            self._validate_phone_number_update(update_data, farmer)
            
            # Update farmer basic fields
            updated_farmer = self._update_farmer_fields(farmer, update_data)
            
            # Update address if provided
            address = self._update_farmer_address(updated_farmer, update_data)
            
            # Update legal documents if provided
            legal_documents = self._update_farmer_legal_documents(update_data)

            return self._convert_farmer_to_read(updated_farmer, address, legal_documents)
            
        except ValueError as e:
            logging.error(f"Error while creating farmer {str(e)}")
            raise ErrorFactory.bad_request(
                message=str(e),
                context={
                    "farmer_service":"create_farmer"
                }
            )


    def delete_farmer(self, farmer_id: uuid.UUID) -> bool:
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

    def deactivate_farmer(self, farmer_id: uuid.UUID) -> bool:
        """Deactivate a farmer"""
        return self.repository.deactivate_farmer(farmer_id)

    def activate_farmer(self, farmer_id: uuid.UUID) -> bool:
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
        address_update_dict = self._build_address_update_dict(update_data)
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
        document_update_dict = self._build_legal_document_update_dict(update_data)
        document = self.repository.update_legal_document(document_id, document_update_dict)
        return self._convert_legal_document_to_read(document) if document else None

    def delete_legal_document(self, document_id: str) -> bool:
        """Delete a legal document"""
        return self.repository.delete_legal_document(document_id)

    def create_farmer_contract(self, contract_data: FarmerContractCreate):
        try:
            self.repository.add_farmer_contract(contract_data=contract_data.dict())
        except Exception as e:
            raise ErrorFactory.internal_server_error(
                user_message="Failed to save farmer contract. Please try again",
                log_message=str(e),
                context="farmer_service:create_farmer_contract"
            )


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
        farmer_reads = [self._build_farmer_read(farmer) for farmer in farmers]
        return FarmerList(farmers=farmer_reads)

    def get_farmers_by_registration_date_range(self, start_date: datetime, end_date: datetime) -> FarmerList:
        """Get farmers registered within a date range"""
        farmers = self.repository.get_farmers_by_registration_date_range(start_date, end_date)
        farmer_reads = [self._build_farmer_read(farmer) for farmer in farmers]
        return FarmerList(farmers=farmer_reads)

    def get_farmers_by_educational_background(self, education: str) -> FarmerList:
        """Get farmers by educational background"""
        farmers = self.repository.get_farmers_by_educational_background(education)
        farmer_reads = [self._build_farmer_read(farmer) for farmer in farmers]
        return FarmerList(farmers=farmer_reads)

    def _get_farmer_address(self, farmer):
        """Get farmer's address if it exists"""
        if not farmer.address_id:
            return None
        return self.repository.get_address_by_id(str(farmer.address_id))

    def _build_farmer_read(self, farmer) -> FarmerRead:
        """Build a complete FarmerRead object with relationships"""
        address = self._get_farmer_address(farmer)
        legal_documents = self.repository.get_legal_documents_by_farmer(str(farmer.id))
        return self._convert_farmer_to_read(farmer, address, legal_documents)

    def _validate_phone_number_update(self, update_data: FarmerUpdate, farmer):
        """Validate phone number uniqueness during update"""
        if not update_data.phone_number or update_data.phone_number == farmer.phone_number:
            return
        
        existing_farmer = self.repository.get_farmer_by_phone(update_data.phone_number)
        if existing_farmer and str(existing_farmer.id) != str(update_data.id):
            raise ValueError("A farmer with this phone number already exists")

    def _build_farmer_update_dict(self, update_data: FarmerUpdate) -> dict:
        """Build farmer update dictionary from update data"""
        update_dict = {}
        fields = ['full_name', 'gender', 'educational_background', 'phone_number']
        
        for field in fields:
            value = getattr(update_data, field, None)
            if value is not None:
                update_dict[field] = value
        
        return update_dict

    def _update_farmer_fields(self, farmer, update_data: FarmerUpdate):
        """Update farmer basic fields"""
        farmer_update_dict = self._build_farmer_update_dict(update_data)
        if farmer_update_dict:
            return self.repository.update_farmer(str(farmer.id), farmer_update_dict)
        return farmer

    def _update_farmer_address(self, farmer, update_data: FarmerUpdate):
        """Update farmer's address if address data is provided"""
        if not update_data.address or not farmer.address_id:
            return self._get_farmer_address(farmer)

        address_update_dict = self._build_address_update_dict(update_data.address)
        if address_update_dict:
            return self.repository.update_address(str(farmer.address_id), address_update_dict)
        
        return self.repository.get_address_by_id(str(farmer.address_id))

    def _update_farmer_legal_documents(self, update_data: FarmerUpdate) -> list:
        """Update farmer's legal documents by replacing all existing ones"""
        if update_data.legal_documents is None:
            return self.repository.get_legal_documents_by_farmer(update_data.id)

        # Remove existing documents
        self._remove_existing_legal_documents(update_data.id)
        
        # Create new documents
        return self._create_legal_documents_for_farmer(update_data.id, update_data.legal_documents)

    def _remove_existing_legal_documents(self, farmer_id):
        """Remove all existing legal documents for a farmer"""
        existing_docs = self.repository.get_legal_documents_by_farmer(farmer_id)
        for doc in existing_docs:
            self.repository.delete_legal_document(str(doc.id))

    def _create_legal_documents_for_farmer(self, farmer_id, legal_documents_data) -> list:
        """Create new legal documents for a farmer"""
        legal_documents = []
        for doc_data in legal_documents_data:
            document_data = {
                'farmer_id': farmer_id,
                'document_type': doc_data.document_type,
                'document_url': doc_data.document_url,
                'issue_date': doc_data.issue_date
            }
            document = self.repository.create_legal_document(document_data)
            legal_documents.append(document)
        return legal_documents

    def _build_address_update_dict(self, address_update: AddressUpdate) -> dict:
        """Build address update dictionary from update data"""
        update_dict = {}
        fields = ['zone_or_sub_city', 'kebele', 'woreda']
        
        for field in fields:
            value = getattr(address_update, field, None)
            if value is not None:
                update_dict[field] = value
        
        return update_dict

    def _build_legal_document_update_dict(self, document_update: LegalDocumentUpdate) -> dict:
        """Build legal document update dictionary from update data"""
        update_dict = {}
        fields = ['document_type', 'document_url', 'issue_date']
        
        for field in fields:
            value = getattr(document_update, field, None)
            if value is not None:
                update_dict[field] = value
        
        return update_dict

    # ====================== CONVERSION HELPER METHODS ======================
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