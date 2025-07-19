from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from app.adapters.farmers.models import (
    Farmer, 
    Address, 
    LegalDocument, 
    Gender, 
    VerificationStatus
)


class IFarmerRepository(ABC):
    # ====================== FARMER OPERATIONS ======================
    
    @abstractmethod
    def create_farmer(self, farmer_data: dict) -> Farmer:
        """
        Create a new farmer record.
        
        Args:
            farmer_data: Dictionary containing farmer information
            
        Returns:
            Farmer: The created farmer instance
            
        Raises:
            ValidationError: If farmer data is invalid
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_farmer_by_id(self, farmer_id: str) -> Optional[Farmer]:
        """
        Retrieve a farmer by their unique identifier.
        
        Args:
            farmer_id: Unique identifier for the farmer
            
        Returns:
            Optional[Farmer]: The farmer instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_farmer_by_phone(self, phone_number: str) -> Optional[Farmer]:
        """
        Retrieve a farmer by their phone number.
        
        Args:
            phone_number: Phone number of the farmer
            
        Returns:
            Optional[Farmer]: The farmer instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all_farmers(self) -> List[Farmer]:
        """
        Retrieve all farmers in the system.
        
        Returns:
            List[Farmer]: List of all farmer instances
        """
        pass

    @abstractmethod
    def update_farmer(self, farmer_id: str, update_data: dict) -> Optional[Farmer]:
        """
        Update existing farmer information.
        
        Args:
            farmer_id: Unique identifier for the farmer
            update_data: Dictionary containing updated fields
            
        Returns:
            Optional[Farmer]: Updated farmer instance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_farmer(self, farmer_id: str) -> bool:
        """
        Permanently delete a farmer record.
        
        Args:
            farmer_id: Unique identifier for the farmer
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    @abstractmethod
    def activate_farmer(self, farmer_id: str) -> bool:
        """
        Activate a farmer account.
        
        Args:
            farmer_id: Unique identifier for the farmer
            
        Returns:
            bool: True if activation was successful, False otherwise
        """
        pass

    @abstractmethod
    def deactivate_farmer(self, farmer_id: str) -> bool:
        """
        Deactivate a farmer account.
        
        Args:
            farmer_id: Unique identifier for the farmer
            
        Returns:
            bool: True if deactivation was successful, False otherwise
        """
        pass

    # ====================== ADDRESS OPERATIONS ======================

    @abstractmethod
    def create_address(self, address_data: dict) -> Address:
        """
        Create a new address record.
        
        Args:
            address_data: Dictionary containing address information
            
        Returns:
            Address: The created address instance
        """
        pass

    @abstractmethod
    def get_address_by_id(self, address_id: str) -> Optional[Address]:
        """
        Retrieve an address by its unique identifier.
        
        Args:
            address_id: Unique identifier for the address
            
        Returns:
            Optional[Address]: The address instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_address_by_farmer(self, farmer_id: str) -> Optional[Address]:
        """
        Retrieve the address associated with a specific farmer.
        
        Args:
            farmer_id: Unique identifier for the farmer
            
        Returns:
            Optional[Address]: The farmer's address if found, None otherwise
        """
        pass

    @abstractmethod
    def update_address(self, address_id: str, update_data: dict) -> Optional[Address]:
        """
        Update existing address information.
        
        Args:
            address_id: Unique identifier for the address
            update_data: Dictionary containing updated fields
            
        Returns:
            Optional[Address]: Updated address instance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_address(self, address_id: str) -> bool:
        """
        Delete an address record.
        
        Args:
            address_id: Unique identifier for the address
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    # ====================== LEGAL DOCUMENT OPERATIONS ======================

    @abstractmethod
    def create_legal_document(self, document_data: dict) -> LegalDocument:
        pass

    @abstractmethod
    def get_legal_document_by_id(self, document_id: str) -> Optional[LegalDocument]:
        pass

    @abstractmethod
    def get_legal_documents_by_farmer(self, farmer_id: str) -> List[LegalDocument]:
        pass

    @abstractmethod
    def get_legal_documents_by_type(self, farmer_id: str, document_type: str) -> List[LegalDocument]:
        pass

    @abstractmethod
    def update_legal_document(self, document_id: str, update_data: dict) -> Optional[LegalDocument]:
        pass

    @abstractmethod
    def delete_legal_document(self, document_id: str) -> bool:
        pass



    @abstractmethod
    def get_farmer_with_relationships(self, farmer_id: str) -> Optional[Farmer]:
        pass

    @abstractmethod
    def activate_farmer(self, farmer_id: str):
        pass

    @abstractmethod
    def deactivate_farmer(self, farmer_id: str):
        pass

    # ====================== SEARCH AND FILTER OPERATIONS ======================

    @abstractmethod
    def search_farmers_by_name(self, name: str) -> List[Farmer]:
        pass

    @abstractmethod
    def get_farmers_by_registration_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Farmer]:
        pass