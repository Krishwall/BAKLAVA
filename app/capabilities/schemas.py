from datetime import datetime

from pydantic import BaseModel

from app.core.enums import RiskLevel


class CapabilityCreate(BaseModel):
    capability_id: str
    name: str
    description: str | None = None
    version: str
    risk_level: RiskLevel = RiskLevel.MEDIUM


class CapabilityResponse(CapabilityCreate):
    created_at: datetime
    updated_at: datetime
