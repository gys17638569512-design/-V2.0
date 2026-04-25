"""M03 add bootstrap state guard for initial admin initialization.

Revision ID: 202604250004
Revises: 202604250003
Create Date: 2026-04-25 16:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202604250004"
down_revision: str | None = "202604250003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bootstrap_states",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_bootstrap_states")),
    )


def downgrade() -> None:
    op.drop_table("bootstrap_states")
