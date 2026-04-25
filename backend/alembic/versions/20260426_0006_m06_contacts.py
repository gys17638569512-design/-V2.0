"""M06 add contacts foundation table.

Revision ID: 202604260006
Revises: 202604250005
Create Date: 2026-04-26 00:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202604260006"
down_revision: str | None = "202604250005"
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
        "contacts",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("mobile", sa.String(length=32), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("position", sa.String(length=64), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "active_primary_customer_id",
            sa.Integer(),
            sa.Computed(
                "CASE WHEN is_primary = 1 AND is_active = 1 THEN customer_id ELSE NULL END",
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
            name=op.f("fk_contacts_customer_id_customers"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contacts")),
    )
    op.create_index(op.f("ix_contacts_customer_id"), "contacts", ["customer_id"], unique=False)
    op.create_index(op.f("ix_contacts_is_active"), "contacts", ["is_active"], unique=False)
    op.create_index("ix_contacts_customer_id_mobile", "contacts", ["customer_id", "mobile"], unique=True)
    op.create_index(
        "uq_contacts_active_primary_customer_id",
        "contacts",
        ["active_primary_customer_id"],
        unique=True,
    )

    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _create_sqlite_updated_at_trigger("contacts")
    else:
        _create_mysql_updated_at_trigger("contacts")


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _drop_sqlite_updated_at_trigger("contacts")
    else:
        _drop_mysql_updated_at_trigger("contacts")

    op.drop_index("uq_contacts_active_primary_customer_id", table_name="contacts")
    op.drop_index("ix_contacts_customer_id_mobile", table_name="contacts")
    op.drop_index(op.f("ix_contacts_is_active"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_customer_id"), table_name="contacts")
    op.drop_table("contacts")
