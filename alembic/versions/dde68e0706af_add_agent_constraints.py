from collections.abc import Sequence

from alembic import op

revision: str = "dde68e0706af"
down_revision: str | Sequence[str] | None = "d138ef3f79ee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_agents_status",
        "agents",
        "status IN ('active', 'suspended', 'deregistered')",
    )
    op.create_check_constraint(
        "ck_agents_environment",
        "agents",
        "environment IN ('dev', 'test', 'qa', 'ppd', 'prod')",
    )
    op.create_check_constraint(
        "ck_agents_risk_level",
        "agents",
        "risk_level IN ('low', 'medium', 'high', 'critical')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_agents_risk_level", "agents", type_="check")
    op.drop_constraint("ck_agents_environment", "agents", type_="check")
    op.drop_constraint("ck_agents_status", "agents", type_="check")
