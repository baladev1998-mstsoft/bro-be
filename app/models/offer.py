import uuid
from sqlalchemy import Column, String, Boolean, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    code = Column(String, unique=True)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    discount = Column(JSONB) # {type:'percent'|'fixed', value:10}
    applicable_to = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
