from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AgentTool(Base):
    __tablename__ = "agent_tools"

    agent_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("agents.agent_id", ondelete="CASCADE"),
        primary_key=True,
    )

    tool_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("tools.tool_id", ondelete="CASCADE"),
        primary_key=True,
    )
