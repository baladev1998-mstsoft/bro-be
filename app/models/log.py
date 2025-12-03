from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.models.base import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String, index=True)
    logger = Column(String, index=True)
    message = Column(Text)
    module = Column(String, nullable=True)
    func_name = Column(String, nullable=True)
    line_no = Column(Integer, nullable=True)
    context = Column(JSON, nullable=True)
    duration = Column(String, nullable=True)
