"""M09 add equipment certificates foundation table.

Revision ID: 202604260009
Revises: 202604260008
Create Date: 2026-04-26 03:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202604260009"
down_revision: str | None = "202604260008"
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
        "equipment_certificates",
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("certificate_no", sa.String(length=128), nullable=True),
        sa.Column("issuer", sa.String(length=128), nullable=True),
        sa.Column("issued_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
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
            ["equipment_id"],
            ["equipment.id"],
            name=op.f("fk_equipment_certificates_equipment_id_equipment"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_equipment_certificates")),
    )
    op.create_index(op.f("ix_equipment_certificates_equipment_id"), "equipment_certificates", ["equipment_id"], unique=False)
    op.create_index(op.f("ix_equipment_certificates_is_active"), "equipment_certificates", ["is_active"], unique=False)

    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _create_sqlite_updated_at_trigger("equipment_certificates")
    else:
        _create_mysql_updated_at_trigger("equipment_certificates")


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _drop_sqlite_updated_at_trigger("equipment_certificates")
    else:
        _drop_mysql_updated_at_trigger("equipment_certificates")

    op.drop_index(op.f("ix_equipment_certificates_is_active"), table_name="equipment_certificates")
    op.drop_index(op.f("ix_equipment_certificates_equipment_id"), table_name="equipment_certificates")
    op.drop_table("equipment_certificates")
