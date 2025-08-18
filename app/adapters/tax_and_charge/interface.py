from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.adapters.tax_and_charge.models import Tax

class ITaxRepository(ABC):
    @abstractmethod
    def get_tax(self, tax_id: UUID) -> Optional[Tax]:
        pass
    
    @abstractmethod
    def list_taxes(self, tax_type: Optional[str] = None) -> List[Tax]:
        pass

    @abstractmethod
    def create_tax(self, tax: dict) -> Optional[Tax]:
        pass

    @abstractmethod
    def update_tax(self, tax_id: UUID, tax: dict) -> Tax:
        pass

    @abstractmethod
    def delete_tax(self, tax_id: UUID) -> None:
        pass
    
    @abstractmethod
    def search_taxes(self, query: str)->List[Tax]:
        pass
