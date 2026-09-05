from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AgentCapability(Base):
    __tablename__ = "agent_capabilities"

    agent_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("agents.agent_id", ondelete="CASCADE"),
        primary_key=True,
    )

    capability_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("capabilities.capability_id", ondelete="CASCADE"),
        primary_key=True,
    )