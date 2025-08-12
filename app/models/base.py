from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Text, DECIMAL, Boolean

import uuid

from app.database import Base


class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
