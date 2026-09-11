from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    approval_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )
    agent_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("agents.agent_id", ondelete="CASCADE"),
        nullable=False,
    )
    tool_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("tools.tool_id", ondelete="CASCADE"),
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    environment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
