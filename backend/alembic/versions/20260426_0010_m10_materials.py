"""M10 add materials foundation table.

Revision ID: 202604260010
Revises: 202604260009
Create Date: 2026-04-26 17:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202604260010"
down_revision: str | None = "202604260009"
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
        "materials",
        sa.Column("system_no", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("specification", sa.String(length=255), nullable=False),
        sa.Column("equipment_category", sa.String(length=128), nullable=False),
        sa.Column("sale_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("cost_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("stock_qty", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("min_stock_qty", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("manufacturer", sa.String(length=128), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_materials")),
    )
    op.create_index(op.f("ix_materials_is_active"), "materials", ["is_active"], unique=False)
    op.create_index(op.f("uq_materials_system_no"), "materials", ["system_no"], unique=True)

    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _create_sqlite_updated_at_trigger("materials")
    else:
        _create_mysql_updated_at_trigger("materials")


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _drop_sqlite_updated_at_trigger("materials")
    else:
        _drop_mysql_updated_at_trigger("materials")

    op.drop_index(op.f("uq_materials_system_no"), table_name="materials")
    op.drop_index(op.f("ix_materials_is_active"), table_name="materials")
    op.drop_table("materials")
