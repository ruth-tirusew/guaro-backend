from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    select,
    func,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel


class CollectionDetail(BaseModel):
    __tablename__ = 'collection_details'

    crop_id = Column(PG_UUID, ForeignKey('crops.id'), nullable=False)
    farmer_id = Column(PG_UUID, ForeignKey('farmers.id'), nullable=False)
    specific_locality = Column(Text)
    parts_accessed = Column(Text)
    annual_collection_capacity = Column(String(255))
    harvest_season = Column(String(255))
    community_knowledge = Column(Text)
    collection_method = Column(String(255))
    period_of_collection = Column(String(255))
    notes = Column(Text)

    crop = relationship("Crop", back_populates="collections")

    def __repr__(self):
        return f"CollectionDetail(id={self.id}, crop={self.crop.scientific_name}, farmer={self.farmer.name})"


class Crop(BaseModel):
    __tablename__ = "crops"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    variety: Mapped[str] = mapped_column(String(50), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0) #move price
    initial_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    harvest_season: Mapped[str] = mapped_column(Text, nullable=True)
    locality: Mapped[str] = mapped_column(Text, nullable=True)
    alternative_locality: Mapped[str] = mapped_column(Text, nullable=True)
    accessible_resources: Mapped[str] = mapped_column(Text, nullable=True)

    initial_records = relationship("InitialBiodata", back_populates="crop")
    price_ledger = relationship("CropPriceLedger", back_populates="crop", cascade="all, delete-orphan")
    receiving_transactions = relationship("GoodsReceiving", back_populates="crop")

    collections = relationship("CollectionDetail", back_populates="crop")

    crop_warehouse = relationship(
        "CropWarehouse",
        back_populates="crop",
        cascade="all, delete-orphan",
        overlaps="warehouses, crop_warehouse"
    )
    warehouses = relationship(
        "Warehouse",
        secondary="crop_warehouse",
        back_populates="crops",
        overlaps="crop_warehouse",
        viewonly=True
    )

    product_crop = relationship(
        "ProductCrop",
        back_populates="crop",
        cascade="all, delete-orphan"
    )
    products = relationship(
        "Product",
        secondary="product_crops",
        back_populates="raw_materials",
        overlaps="product_crop",
        viewonly=True
    )

    @hybrid_property
    def total_available(self):
        """Return total available amount in warehouses (in-memory)."""
        return sum(cw.current_amount for cw in self.crop_warehouse)

    @total_available.expression
    def total_available(cls):
        """SQL expression to calculate total available amount (database-level)."""
        try:
            return (
                select(func.coalesce(func.sum(CropWarehouse.current_amount), 0.0))
                .where(CropWarehouse.crop_id == cls.id)
                .label("total_available")
            )
        except Exception as e:
            print(e)




class CropPriceLedger(BaseModel):
    __tablename__ = "crop_price_ledger"

    previous_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    updated_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    crop_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)

    crop: Mapped["Crop"] = relationship("Crop", back_populates="price_ledger")


class GoodsReceiving(BaseModel):
    __tablename__ = "goods_receiving"

    batch_number = Column(String(100), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    notes: Mapped[str] = mapped_column(String(255), nullable=True)

    crop_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    warehouse_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    farmer_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)

    crop: Mapped["Crop"] = relationship("Crop", back_populates="receiving_transactions")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
    farmer: Mapped["Farmer"] = relationship("Farmer")


class CropAmountLedger(BaseModel):
    __tablename__ = "crop_amount_ledger"

    previous_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    updated_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    receiving_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("goods_receiving.id"), nullable=True)
    warehouse_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)


class InitialBiodata(BaseModel):
    __tablename__ = "initial_biodata"

    farmer_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)

    average_yield_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    last_harvest_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    land_area_sourced_from = Column(String(255))
    notes = Column(Text)

    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="initial_biodata")
    crop: Mapped["Crop"] = relationship("Crop", back_populates="initial_records")



class CropWarehouse(BaseModel):
    __tablename__ = 'crop_warehouse'

    crop_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), primary_key=True
    )
    warehouse_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey('warehouses.id', ondelete='CASCADE'), primary_key=True
    )

    current_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    crop: Mapped["Crop"] = relationship("Crop", back_populates="crop_warehouse", overlaps="crops")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="crop_warehouse", overlaps="warehouses", viewonly=True)