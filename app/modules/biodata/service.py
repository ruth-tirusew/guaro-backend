from typing import List, Optional
import uuid
from datetime import datetime

from app.adapters.biodata.interface import IBiodataRepository
from app.modules.biodata.schemas import (
    CropCreate, CropUpdate, CropRead,
    InitialBiodataCreate, InitialBiodataUpdate, InitialBiodataRead
)
from app.modules.farmers.service import FarmerService

class BiodataService:
    def __init__(self, farmer_service: FarmerService, biodata_repository: IBiodataRepository):
        self.repository = biodata_repository
        self.farmer_service  = farmer_service

    # Crop methods
    def create_crop(self, crop_data: CropCreate) -> CropRead:
        crop = self.repository.create_crop(crop_data.model_dump())
        return CropRead.model_validate(crop)

    def get_crop_by_id(self, crop_id: uuid.UUID) -> Optional[CropRead]:
        crop = self.repository.get_crop_by_id(crop_id)
        return CropRead.model_validate(crop) if crop else None

    def get_all_crops(self) -> List[CropRead]:
        crops = self.repository.get_all_crops()
        return [CropRead.model_validate(crop) for crop in crops]

    def update_crop(self, crop_id: uuid.UUID, update_data: CropUpdate) -> Optional[CropRead]:
        crop = self.repository.update_crop(crop_id, update_data.model_dump(exclude_unset=True))
        return CropRead.model_validate(crop) if crop else None

    def delete_crop(self, crop_id: uuid.UUID) -> bool:
        return self.repository.delete_crop(crop_id)

    # InitialBiodata methods
    def create_initial_biodata(self, biodata_data: InitialBiodataCreate) -> InitialBiodataRead:
        # Validate farmer existence
        farmer_id = str(biodata_data.farmer_id)
        farmer = self.farmer_service.get_farmer(farmer_id)
        if not farmer:
            raise ValueError(f"Farmer with id {farmer_id} does not exist")
        biodata = self.repository.create_initial_biodata(biodata_data.model_dump())
        return InitialBiodataRead.model_validate(biodata)

    def get_initial_biodata_by_id(self, biodata_id: uuid.UUID) -> Optional[InitialBiodataRead]:
        biodata = self.repository.get_initial_biodata_by_id(biodata_id)
        return InitialBiodataRead.model_validate(biodata) if biodata else None

    def get_initial_biodata_by_farmer(self, farmer_id: uuid.UUID) -> List[InitialBiodataRead]:
        biodata_list = self.repository.get_initial_biodata_by_farmer(farmer_id)
        return [InitialBiodataRead.model_validate(b) for b in biodata_list]

    def get_initial_biodata_by_crop(self, crop_id: uuid.UUID) -> List[InitialBiodataRead]:
        biodata_list = self.repository.get_initial_biodata_by_crop(crop_id)
        return [InitialBiodataRead.model_validate(b) for b in biodata_list]

    def update_initial_biodata(self, biodata_id: uuid.UUID, update_data: InitialBiodataUpdate) -> Optional[InitialBiodataRead]:
        biodata = self.repository.update_initial_biodata(biodata_id, update_data.model_dump(exclude_unset=True))
        return InitialBiodataRead.model_validate(biodata) if biodata else None

    def delete_initial_biodata(self, biodata_id: uuid.UUID) -> bool:
        return self.repository.delete_initial_biodata(biodata_id)


