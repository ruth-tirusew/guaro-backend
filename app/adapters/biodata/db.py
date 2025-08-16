from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.adapters.biodata.interface import IBiodataRepository
from app.adapters.biodata.models import Crop, InitialBiodata, CropAmountLedger, CropPriceLedger, GoodsReceiving, CropWarehouse

class BiodataRepository(IBiodataRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_crop(self, crop_data: dict) -> Crop:
        try:
            crop = Crop(**crop_data)
            self.db.add(crop)
            self.db.commit()
            self.db.refresh(crop)
            return crop
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Crop creation failed")

    def get_crop_by_id(self, crop_id: UUID) -> Optional[Crop]:
        return (
            self.db.query(Crop)
            .options(joinedload(Crop.receiving_transactions))
            .filter(Crop.id == crop_id)
            .first()
        )


    def get_all_crops(self) -> List[Crop]:
        return self.db.query(Crop).all()

    def update_crop(self, crop_id: UUID, update_data: dict) -> Optional[Crop]:
        crop = self.get_crop_by_id(crop_id)
        if not crop:
            return None
        try:
            for key, value in update_data.items():
                if hasattr(crop, key):
                    setattr(crop, key, value)
            self.db.commit()
            self.db.refresh(crop)
            return crop
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Crop update failed")

    def delete_crop(self, crop_id: UUID) -> bool:
        crop = self.get_crop_by_id(crop_id)
        if crop:
            crop.is_deleted=True
            self.db.commit()
            return True
        return False

    def create_initial_biodata(self, biodata_data: dict) -> InitialBiodata:
        try:
            biodata = InitialBiodata(**biodata_data)
            self.db.add(biodata)
            self.db.commit()
            self.db.refresh(biodata)
            return biodata
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="InitialBiodata creation failed")

    def get_initial_biodata_by_id(self, biodata_id: UUID) -> Optional[InitialBiodata]:
        return self.db.query(InitialBiodata).filter(InitialBiodata.id == biodata_id).first()

    def get_initial_biodata_by_farmer(self, farmer_id: UUID) -> List[InitialBiodata]:
        return self.db.query(InitialBiodata).filter(InitialBiodata.farmer_id == farmer_id).all()

    def get_initial_biodata_by_crop(self, crop_id: UUID) -> List[InitialBiodata]:
        return self.db.query(InitialBiodata).filter(InitialBiodata.crop_id == crop_id).all()

    def update_initial_biodata(self, biodata_id: UUID, update_data: dict) -> Optional[InitialBiodata]:
        biodata = self.get_initial_biodata_by_id(biodata_id)
        if not biodata:
            return None
        try:
            for key, value in update_data.items():
                if hasattr(biodata, key):
                    setattr(biodata, key, value)
            self.db.commit()
            self.db.refresh(biodata)
            return biodata
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="InitialBiodata update failed")

    def delete_initial_biodata(self, biodata_id: UUID) -> bool:
        biodata = self.get_initial_biodata_by_id(biodata_id)
        if biodata:
            biodata.is_deleted=True
            self.db.commit()
            return True
        return False

    def update_price(self, crop_id: UUID, new_price: float) -> Crop:
        db_crop = self.get_crop_by_id(crop_id)
        if not db_crop:
            raise ValueError("Crop not found")
        
        CropPriceLedger(
            previous_price = db_crop.price,
            updated_price  = new_price,
            crop_id = crop_id
        )
        
        db_crop.price = new_price
        self.db.commit()
        self.db.refresh(db_crop)
        return db_crop


    def receive(self, crop_id: UUID, amount: float, warehouse_id: UUID, farmer_id: UUID, notes: Optional[str] = None) -> Crop:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        db_crop = self.db.query(Crop).filter(Crop.id == crop_id, Crop.is_deleted == False).first()
        if not db_crop:
            raise ValueError("Crop not found")

        crop_warehouse = (
            self.db.query(CropWarehouse)
            .filter(CropWarehouse.crop_id == crop_id, CropWarehouse.warehouse_id == warehouse_id)
            .first()
        )

        previous_amount = crop_warehouse.current_amount if crop_warehouse else 0.0
        new_amount = float(previous_amount) + amount

        if crop_warehouse:
            crop_warehouse.current_amount = new_amount
        else:
            crop_warehouse = CropWarehouse(
                crop_id=crop_id,
                warehouse_id=warehouse_id,
                current_amount=new_amount
            )
            self.db.add(crop_warehouse)
        sequence_number = self.get_next_sequence_number(crop_id)
        batch_number = self.generate_batch_number(db_crop, sequence_number)
        receiving = GoodsReceiving(
            batch_number=batch_number,
            quantity=amount,
            transaction_date=datetime.now(),
            notes=notes,
            crop_id=crop_id,
            warehouse_id=warehouse_id,
            farmer_id=farmer_id
        )
        self.db.add(receiving)
        self.db.flush() 

        amount_ledger = CropAmountLedger(
            previous_amount=previous_amount,
            updated_amount=new_amount,
            receiving_id=receiving.id,
            warehouse_id=warehouse_id
        )
        self.db.add(amount_ledger)

        # Commit all changes
        self.db.commit()
        self.db.refresh(db_crop)
        return db_crop


    def deplete(self, crop_id: UUID, amount: float, warehouse_id: UUID, notes: Optional[str] = None) -> Crop:
        """
        Deplete (remove) a certain amount of crop from a warehouse.
        Raises an error if insufficient stock.
        """
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        db_crop = self.db.query(Crop).filter(Crop.id == crop_id, Crop.is_deleted == False).first()
        if not db_crop:
            raise ValueError("Crop not found")

        crop_warehouse = (
            self.db.query(CropWarehouse)
            .filter(CropWarehouse.crop_id == crop_id, CropWarehouse.warehouse_id == warehouse_id)
            .first()
        )

        if not crop_warehouse:
            raise ValueError("No inventory found for this crop in the specified warehouse")

        if crop_warehouse.current_amount < amount:
            raise ValueError(f"Insufficient stock. Available: {crop_warehouse.current_amount}, Requested: {amount}")

        previous_amount = float(crop_warehouse.current_amount)
        new_amount = previous_amount - amount
        crop_warehouse.current_amount = new_amount

        amount_ledger = CropAmountLedger(
            previous_amount=previous_amount,
            updated_amount=new_amount,
            receiving_id=None, 
            warehouse_id=warehouse_id
        )
        self.db.add(amount_ledger)

        self.db.commit()
        self.db.refresh(db_crop)
        return db_crop


    def generate_batch_number(self, crop: Crop, sequence_number: int) -> str:
        formatted_name = crop.name.replace(" ", "_").upper()
        transaction_date = datetime.now().strftime("%Y%m%d")
        return f"BATCH-{formatted_name}-{transaction_date}-{sequence_number:03}"

    def get_next_sequence_number(self, crop_id: UUID) -> int:
        latest_receiving = (
            self.db.query(GoodsReceiving)
            .filter(GoodsReceiving.crop_id == crop_id)
            .order_by(GoodsReceiving.batch_number.desc())
            .first()
        )

        if latest_receiving and latest_receiving.batch_number:
            parts = latest_receiving.batch_number.split("-")
            if len(parts) == 4:
                try:
                    last_sequence = int(parts[-1])
                    return last_sequence + 1
                except ValueError:
                    return 1
        return 1 