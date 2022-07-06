import enum
from sqlalchemy import Column, Integer, Enum, SmallInteger, Float, DateTime, String
from sqlalchemy.sql import func

from .base import Base

class DocumentStatus(enum.Enum):
    processing = 1
    success = 2
    error = 3

class Document(Base):

    __tablename__ = "document"

    id = Column(Integer, primary_key=True)
    status = Column(Enum(DocumentStatus), nullable=False)
    page_count = Column(SmallInteger)
    received_at = Column(DateTime, server_default=func.now())
    processing_time = Column(Float, comment="in seconds")
    input_hash = Column(String(length=50), nullable=False, comment="SHA1")

    def __repr__(self):
        return f"<Document(id={self.id}, " \
               f"status={self.status}, " \
               f"page_count={self.page_count}"
