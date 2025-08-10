# server/models.py
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Machine(Base):
    __tablename__ = "machines"
    machine_id = Column(String, primary_key=True, index=True)
    hostname = Column(String, nullable=True)
    os_name = Column(String, nullable=True)
    os_version = Column(String, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    latest_payload = Column(Text, nullable=True)  # JSON text of last report

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    payload = Column(Text, nullable=False)
