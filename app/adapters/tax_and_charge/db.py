from app.adapters.tax_and_charge.interface import ITaxRepository
from app.adapters.tax_and_charge.models import Tax

class TaxRepository(ITaxRepository): 
    def get_tax(self, tax_id: UUID) -> Optional[Tax]:
        """Get a single tax by ID"""
        return self.db.query(Tax).filter(
            Tax.id == tax_id,
            Tax.is_deleted == False
        ).first()

    def list_taxes(self, tax_type: Optional[str] = None) -> List[Tax]:
        """List all taxes with optional type filtering"""
        query = self.db.query(Tax).filter(Tax.is_deleted == False)
        
        if tax_type:
            query = query.filter(Tax.tax_type == tax_type)
        
        return query.all()

    def create_tax(self, tax_data: dict) -> Tax:
        """Create a new tax"""
        try:
            db_tax = Tax(**tax_data)
            self.db.add(db_tax)
            self.db.commit()
            self.db.refresh(db_tax)
            return db_tax
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))

    def update_tax(self, tax_id: UUID, tax_data: dict) -> Optional[Tax]:
        """Update an existing tax"""
        db_tax = self.get_tax(tax_id)
        if not db_tax:
            raise ValueError("Tax not found")
        
        try:
            for key, value in tax_data.items():
                if key.startswith('_') or key == 'id':
                    continue
                if hasattr(db_tax, key):
                    setattr(db_tax, key, value)
            
            self.db.commit()
            self.db.refresh(db_tax)
            return db_tax
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Tax update failed")

    def delete_tax(self, tax_id: UUID) -> None:
        """Soft delete a tax"""
        db_tax = self.get_tax(tax_id)
        if db_tax:
            db_tax.is_deleted = True
            self.db.commit()
        else:
            raise ValueError("Tax not found")

    def search_taxes(self, query: str) -> List[Tax]:
        """Search taxes by name or description"""
        return self.db.query(Tax).filter(
            Tax.is_deleted == False,
            or_(
                Tax.name.ilike(f"%{query}%"),
                Tax.description.ilike(f"%{query}%") if hasattr(Tax, 'description') else True
            )
        ).all()