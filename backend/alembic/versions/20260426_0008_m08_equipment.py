"""M08 add equipment foundation table.

Revision ID: 202604260008
Revises: 202604260007
Create Date: 2026-04-26 02:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202604260008"
down_revision: str | None = "202604260007"
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
        "equipment",
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("system_no", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("manufacturer", sa.String(length=128), nullable=True),
        sa.Column("manufacture_date", sa.Date(), nullable=True),
        sa.Column("factory_no", sa.String(length=64), nullable=True),
        sa.Column("site_inner_no", sa.String(length=64), nullable=True),
        sa.Column("owner_unit", sa.String(length=128), nullable=True),
        sa.Column("use_unit", sa.String(length=128), nullable=True),
        sa.Column("management_department", sa.String(length=128), nullable=True),
        sa.Column("equipment_admin_name", sa.String(length=128), nullable=True),
        sa.Column("equipment_admin_phone", sa.String(length=32), nullable=True),
        sa.Column("workshop", sa.String(length=128), nullable=True),
        sa.Column("track_no", sa.String(length=64), nullable=True),
        sa.Column("location_detail", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["site_id"],
            ["sites.id"],
            name=op.f("fk_equipment_site_id_sites"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_equipment")),
    )
    op.create_index(op.f("ix_equipment_site_id"), "equipment", ["site_id"], unique=False)
    op.create_index(op.f("ix_equipment_is_active"), "equipment", ["is_active"], unique=False)
    op.create_index("uq_equipment_system_no", "equipment", ["system_no"], unique=True)

    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _create_sqlite_updated_at_trigger("equipment")
    else:
        _create_mysql_updated_at_trigger("equipment")


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _drop_sqlite_updated_at_trigger("equipment")
    else:
        _drop_mysql_updated_at_trigger("equipment")

    op.drop_index("uq_equipment_system_no", table_name="equipment")
    op.drop_index(op.f("ix_equipment_is_active"), table_name="equipment")
    op.drop_index(op.f("ix_equipment_site_id"), table_name="equipment")
    op.drop_table("equipment")
