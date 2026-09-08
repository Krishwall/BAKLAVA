from datetime import datetime

from pydantic import BaseModel


class ToolCreate(BaseModel):
    tool_id: str
    name: str
    description: str | None = None
    version: str
    owner: str
    status: str
    environment: str
    risk_level: str
    endpoint: str | None = None


class ToolResponse(ToolCreate):
    created_at: datetime
    updated_at: datetime
