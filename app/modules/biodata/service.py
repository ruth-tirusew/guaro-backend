from typing import List, Optional
import uuid
from datetime import datetime

from app.adapters.biodata.interface import IBiodataRepository
from app.core.exceptions import APIError, ErrorFactory
from app.modules.biodata.schemas import (
    CropCreate, CropUpdate, CropRead, CropList,
    InitialBiodataCreate, InitialBiodataUpdate, InitialBiodataRead, InitialBiodataList,
    GRNRequest
)
from app.modules.farmers.service import FarmerService

class BiodataService:
    def __init__(self, farmer_service: FarmerService, biodata_repository: IBiodataRepository):
        self.repository = biodata_repository
        self.farmer_service  = farmer_service

    # Crop methods
    def create_crop(self, crop_data: CropCreate) -> CropRead:
        crop = self.repository.create_crop(crop_data.model_dump())
        
        if crop_data.price:
            self.repository.update_price(crop_id=crop.id, new_price=crop_data.price)
        return CropRead.model_validate(crop)

    def get_crop_by_id(self, crop_id: uuid.UUID) -> Optional[CropRead]:
        crop = self.repository.get_crop_by_id(crop_id)
        return CropRead.model_validate(crop) if crop else None

    def get_all_crops(self) -> List[CropRead]:
        crops = self.repository.get_all_crops()
        return CropList(crops=[CropRead.model_validate(crop) for crop in crops])

    def update_crop(self, update_data: CropUpdate) -> Optional[CropRead]:
        crop = self.repository.update_crop(update_data.id, update_data.model_dump(exclude_unset=True))
        if update_data.price:
            self.repository.update_price(crop_id=update_data.id, new_price=update_data.price)

        return CropRead.model_validate(crop) if crop else None

    def delete_crop(self, crop_id: uuid.UUID) -> bool:
        return self.repository.delete_crop(crop_id)


    def receive_crop(self,request: GRNRequest) -> CropRead:
        crop = self.repository.receive(request.crop_id, request.amount, request.warehouse_id, request.farmer_id, request.notes)
        return crop

    
    def deplete_crop(self,request: GRNRequest) -> CropRead:
        self.get_crop_by_id(request.crop_id)
        crop = self.repository.deplete(request.crop_id, request.amount, request.warehouse_id, request.notes)
        return CropRead.model_validate(crop)   

    def create_initial_biodata(self, biodata_data: InitialBiodataCreate) -> InitialBiodataRead:
        farmer = self.farmer_service.get_farmer(biodata_data.farmer_id)
        if not farmer:
            raise ErrorFactory.not_found("Farmer")
        existing_crop = self.get_crop_by_id(biodata_data.crop_id)
        if not existing_crop:
            raise ErrorFactory.not_found("Crop")
        biodata = self.repository.create_initial_biodata(biodata_data.model_dump())
        return InitialBiodataRead.model_validate(biodata)

    def get_initial_biodata_by_id(self, biodata_id: uuid.UUID) -> Optional[InitialBiodataRead]:
        biodata = self.repository.get_initial_biodata_by_id(biodata_id)
        return InitialBiodataRead.model_validate(biodata) if biodata else None

    def get_initial_biodata_by_farmer(self, farmer_id: uuid.UUID) -> InitialBiodataList:
        biodata_list = self.repository.get_initial_biodata_by_farmer(farmer_id)
        return InitialBiodataList(biodata=[InitialBiodataRead.model_validate(b) for b in biodata_list])

    def update_initial_biodata(self, update_data: InitialBiodataUpdate) -> Optional[InitialBiodataRead]:
        existing_biodata = self.get_initial_biodata_by_id(update_data.id)
        if not existing_biodata:
            raise ErrorFactory.not_found("Biodata doesn't exist")
        biodata = self.repository.update_initial_biodata(update_data.id, update_data.model_dump(exclude_unset=True))
        return InitialBiodataRead.model_validate(biodata) if biodata else None

    def delete_initial_biodata(self, biodata_id: uuid.UUID) -> bool:
        existing_biodata = self.get_initial_biodata_by_id(update_data.id)
        if not existing_biodata:
            raise ErrorFactory.not_found("Biodata doesn't exist")

        return self.repository.delete_initial_biodata(biodata_id)


