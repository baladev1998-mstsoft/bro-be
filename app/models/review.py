import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"))
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"))
    rating = Column(Integer, nullable=False)
    title = Column(String)
    comment = Column(Text)
    is_published = Column(Boolean, default=True)

    user = relationship("User", back_populates="reviews")
    property = relationship("Property", back_populates="reviews")
    booking = relationship("Booking", back_populates="reviews")

    __table_args__ = (CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),)
