# server/schemas.py
from pydantic import BaseModel
from typing import Any, Dict, Optional

class ReportPayload(BaseModel):
    machine_id: str
    hostname: Optional[str]
    os: Optional[Dict[str, Any]]
    checks: Dict[str, Any]
    timestamp: str  # ISO-formatted string

class MachineOut(BaseModel):
    machine_id: str
    hostname: Optional[str]
    os_name: Optional[str]
    os_version: Optional[str]
    last_seen: Optional[str]
    latest_payload: Optional[Dict[str, Any]]
