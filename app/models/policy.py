import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Policy(Base):
    __tablename__ = "policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    meta = Column(JSONB, default={})
    is_deleted = Column(Boolean, default=False)

    property_policies = relationship("PropertyPolicy", back_populates="policy")

class PropertyPolicy(Base):
    __tablename__ = "property_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False)
    content = Column(Text)
    short_text = Column(Text)
    effective_from = Column(Date)
    effective_to = Column(Date)

    property = relationship("Property", back_populates="property_policies")
    policy = relationship("Policy", back_populates="property_policies")

    __table_args__ = (UniqueConstraint('property_id', 'policy_id', name='uq_property_policy'),)
