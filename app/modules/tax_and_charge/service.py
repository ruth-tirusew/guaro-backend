from typing import List, Optional
from uuid import UUID
from app.adapters.tax_and_charge.interface import ITaxRepository
from app.modules.tax_and_charge.schemas import Tax, TaxCreate, TaxUpdate, Tax, TaxList
from app.core.exceptions import ErrorFactory


class TaxService:
    def __init__(self, tax_repository: ITaxRepository):
        self.repository = tax_repository

    def create_tax(self, tax_data: TaxCreate) -> Tax:
        """Create a new tax with validation"""
        if self._tax_name_exists(tax_data.name):
            raise ErrorFactory.bad_request(
                message=f"Tax with name '{tax_data.name}' already exists"
            )

        rate_value = tax_data.tax_percentage
        self._validate_tax(tax_data.name, rate_value)
        
        try:
            created = self.repository.create_tax(tax_data.model_dump())
            print(created)
            return Tax.model_validate(created)

        except ValueError as e:
            raise ErrorFactory.bad_request(
                message=str(e)
            )

    def get_tax_by_id(self, tax_id: UUID) -> Tax:
        """Get a single tax by ID"""
        tax = self.repository.get_tax(tax_id)
        if not tax:
            raise ErrorFactory.not_found(
                resource="Tax"
            )
        return Tax.model_validate(tax)

    def list_taxes(self, tax_type: Optional[str] = None) -> TaxList:
        """List all taxes with optional type filtering"""
        taxes = self.repository.list_taxes(tax_type)
        return TaxList(items=[Tax.model_validate(tax) for tax in taxes])

    def update_tax(self, tax_id: UUID, tax_data: TaxUpdate) -> Tax:
        """Update an existing tax"""
        if not self.repository.get_tax(tax_id):
            raise ErrorFactory.not_found(
                resource="Tax"
            )

        if tax_data.name and self._tax_name_exists_excluding_id(tax_data.name, tax_id):
            raise ErrorFactory.bad_request(
                message=f"Tax with name '{tax_data.name}' already exists"
            )
            
        rate_value = getattr(tax_data, "tax_percentage", getattr(tax_data, "rate", None))
        if tax_data.name is not None or rate_value is not None:
            self._validate_tax(tax_data.name, rate_value)
        try:
            update_data = tax_data.model_dump(exclude_none=True)
            updated_tax = self.repository.update_tax(tax_id, update_data)
            return Tax.model_validate(updated_tax)
        except ValueError as e:
            raise ErrorFactory.bad_request(
                message=str(e)
            )

    def delete_tax(self, tax_id: UUID) -> None:
        """Soft delete a tax"""
        if not self.repository.get_tax(tax_id):
            raise ErrorFactory.not_found(
                resource="Tax"
            )
        
        try:
            self.repository.delete_tax(tax_id)
        except ValueError as e:
            raise ErrorFactory.bad_request(
                message=str(e)
            )

    def search_taxes(self, query: str) -> List[Tax]:
        """Search taxes by name or description"""
        if not query or len(query.strip()) < 2:
            raise ErrorFactory.bad_request(
                message="Search query must be at least 2 characters long"
            )
        
        taxes = self.repository.search_taxes(query.strip())
        return [Tax.model_validate(tax) for tax in taxes]

    def get_taxes_by_type(self, tax_type: str) -> List[Tax]:
        """Get all taxes of a specific type"""
        taxes = self.repository.list_taxes(tax_type=tax_type)
        return [Tax.model_validate(tax) for tax in taxes]

    def _tax_name_exists(self, name: str) -> bool:
        """Check if a tax with the given name already exists"""
        taxes = self.repository.search_taxes(name)
        return any(tax.name.lower() == name.lower() for tax in taxes)

    def _tax_name_exists_excluding_id(self, name: str, exclude_id: UUID) -> bool:
        """Check if a tax with the given name exists, excluding a specific ID"""
        taxes = self.repository.search_taxes(name)
        return any(tax.name.lower() == name.lower() and tax.id != exclude_id for tax in taxes)


    def _validate_tax(self, name: Optional[str], rate: Optional[float]) -> None:
        if name is not None:
            cleaned = name.replace(" ", "").replace("_", "").replace("-", "")
            if not (cleaned.isalnum() and 3 <= len(name) <= 50):
                raise ErrorFactory.bad_request(
                    message="Tax name must be alphanumeric and between 3-50 characters"
                )

        if rate is not None:
            try:
                valid = 0 <= rate <= 100
            except TypeError:
                valid = False
            if not valid:
                raise ErrorFactory.bad_request(
                    message="Tax rate must be between 0 and 100"
                )
