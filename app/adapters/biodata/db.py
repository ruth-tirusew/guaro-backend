from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from uuid import UUID
from typing import List, Optional
from app.adapters.biodata.interface import IBiodataRepository
from app.adapters.biodata.models import Crop, InitialBiodata

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
        return self.db.query(Crop).filter(Crop.id == crop_id).first()

    def get_all_crops(self) -> List[Crop]:
        return self.db.query(Crop).all()

    def update_crop(self, crop_id: str, update_data: dict) -> Optional[Crop]:
        crop_uuid = UUID(crop_id)
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
            self.db.delete(crop)
            self.db.commit()
            return True
        return False

    # InitialBiodata methods
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
            self.db.delete(biodata)
            self.db.commit()
            return True
        return False
