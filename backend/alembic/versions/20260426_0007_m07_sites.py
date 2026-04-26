"""M07 add sites foundation table.

Revision ID: 202604260007
Revises: 202604260006
Create Date: 2026-04-26 01:10:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202604260007"
down_revision: str | None = "202604260006"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _create_sqlite_updated_at_trigger(table_name: str) -> None:
    op.execute(
        f"""
        CREATE TRIGGER trg_{table_name}_set_updated_at
        AFTER UPDATE ON {table_name}
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE {table_name}
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END
        """
    )


def _drop_sqlite_updated_at_trigger(table_name: str) -> None:
    op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_set_updated_at")


def _create_mysql_updated_at_trigger(table_name: str) -> None:
    op.execute(
        f"""
        CREATE TRIGGER trg_{table_name}_set_updated_at
        BEFORE UPDATE ON {table_name}
        FOR EACH ROW
        SET NEW.updated_at = CURRENT_TIMESTAMP
        """
    )


def _drop_mysql_updated_at_trigger(table_name: str) -> None:
    op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_set_updated_at")


def upgrade() -> None:
    op.create_table(
        "sites",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("contact_name", sa.String(length=128), nullable=True),
        sa.Column("contact_phone", sa.String(length=32), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "active_name",
            sa.String(length=128),
            sa.Computed(
                "CASE WHEN is_active = 1 THEN name ELSE NULL END",
                persisted=True,
            ),
            nullable=True,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name=op.f("fk_sites_customer_id_customers"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sites")),
    )
    op.create_index(op.f("ix_sites_customer_id"), "sites", ["customer_id"], unique=False)
    op.create_index(op.f("ix_sites_is_active"), "sites", ["is_active"], unique=False)
    op.create_index(
        "uq_sites_active_customer_id_name",
        "sites",
        ["customer_id", "active_name"],
        unique=True,
    )

    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _create_sqlite_updated_at_trigger("sites")
    else:
        _create_mysql_updated_at_trigger("sites")


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _drop_sqlite_updated_at_trigger("sites")
    else:
        _drop_mysql_updated_at_trigger("sites")

    op.drop_index("uq_sites_active_customer_id_name", table_name="sites")
    op.drop_index(op.f("ix_sites_is_active"), table_name="sites")
    op.drop_index(op.f("ix_sites_customer_id"), table_name="sites")
    op.drop_table("sites")
