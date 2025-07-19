from typing import List, Optional
from uuid import uuid4, UUID
from app.adapters.biodata.interface import IBiodataRepository
from app.adapters.biodata.models import Crop, InitialBiodata

class MockBiodataRepository(IBiodataRepository):
    def __init__(self):
        self.crops = {}
        self.initial_biodata = {}

    # Crop methods
    def create_crop(self, crop_data: dict) -> Crop:
        crop_id = uuid4()
        crop = Crop(id=crop_id, **crop_data)
        self.crops[crop_id] = crop
        return crop

    def get_crop_by_id(self, crop_id: UUID) -> Optional[Crop]:
        return self.crops.get(crop_id)

    def get_all_crops(self) -> List[Crop]:
        return list(self.crops.values())

    def update_crop(self, crop_id: UUID, update_data: dict) -> Optional[Crop]:
        crop = self.crops.get(crop_id)
        if not crop:
            return None
        for key, value in update_data.items():
            if hasattr(crop, key):
                setattr(crop, key, value)
        return crop

    def delete_crop(self, crop_id: UUID) -> bool:
        if crop_id in self.crops:
            del self.crops[crop_id]
            return True
        return False
        
    def create_initial_biodata(self, biodata_data: dict) -> InitialBiodata:
        biodata_id = uuid4()
        biodata = InitialBiodata(id=biodata_id, **biodata_data)
        self.initial_biodata[biodata_id] = biodata
        return biodata

    def get_initial_biodata_by_id(self, biodata_id: UUID) -> Optional[InitialBiodata]:
        return self.initial_biodata.get(biodata_id)

    def get_initial_biodata_by_farmer(self, farmer_id: UUID) -> List[InitialBiodata]:
        return [b for b in self.initial_biodata.values() if b.farmer_id == farmer_id]

    def get_initial_biodata_by_crop(self, crop_id: UUID) -> List[InitialBiodata]:
        return [b for b in self.initial_biodata.values() if b.crop_id == crop_id]

    def update_initial_biodata(self, biodata_id: UUID, update_data: dict) -> Optional[InitialBiodata]:
        biodata = self.initial_biodata.get(biodata_id)
        if not biodata:
            return None
        for key, value in update_data.items():
            if hasattr(biodata, key):
                setattr(biodata, key, value)
        return biodata

    def delete_initial_biodata(self, biodata_id: UUID) -> bool:
        if biodata_id in self.initial_biodata:
            del self.initial_biodata[biodata_id]
            return True
        return False
