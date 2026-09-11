from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Policy(Base):
    __tablename__ = "policies"

    __table_args__ = (
        CheckConstraint(
            "environment IN ('dev', 'test', 'qa', 'ppd', 'prod')",
            name="ck_policies_environment",
        ),
        CheckConstraint(
            "risk_level IN ('low', 'medium', 'high', 'critical')",
            name="ck_policies_risk_level",
        ),
        CheckConstraint(
            "decision IN ('ALLOW', 'DENY', 'REQUIRE_APPROVAL')",
            name="ck_policies_decision",
        ),
    )

    policy_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
