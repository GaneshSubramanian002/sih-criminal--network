from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .db import Base

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    entity_type = Column(String(50), index=True, nullable=False)
    source = Column(String(255))
    confidence = Column(Float, default=1.0)

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False)
    record_type = Column(String(50), nullable=False)
    raw_text = Column(Text)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False)
    from_entity = Column(String(255), nullable=False)
    to_entity = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=True)

class CDR(Base):
    __tablename__ = "cdrs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False)
    caller = Column(String(255), nullable=False)
    receiver = Column(String(255), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=True)