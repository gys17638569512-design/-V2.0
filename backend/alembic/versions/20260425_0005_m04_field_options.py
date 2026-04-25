"""M04 add field options foundation table and seed baseline options.

Revision ID: 202604250005
Revises: 202604250004
Create Date: 2026-04-25 18:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202604250005"
down_revision: str | None = "202604250004"
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
        "field_options",
        sa.Column("field_key", sa.String(length=64), nullable=False),
        sa.Column("option_value", sa.String(length=64), nullable=False),
        sa.Column("option_label", sa.String(length=128), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_field_options")),
        sa.UniqueConstraint(
            "field_key",
            "option_value",
            name="uq_field_options_field_key_option_value",
        ),
    )
    op.create_index(op.f("ix_field_options_field_key"), "field_options", ["field_key"], unique=False)
    op.create_index(op.f("ix_field_options_is_active"), "field_options", ["is_active"], unique=False)

    field_options_table = sa.table(
        "field_options",
        sa.column("field_key", sa.String(length=64)),
        sa.column("option_value", sa.String(length=64)),
        sa.column("option_label", sa.String(length=128)),
        sa.column("sort_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        field_options_table,
        [
            {"field_key": "device_category", "option_value": "BRIDGE_CRANE", "option_label": "桥式起重机", "sort_order": 10, "is_active": True},
            {"field_key": "device_category", "option_value": "GANTRY_CRANE", "option_label": "门式起重机", "sort_order": 20, "is_active": True},
            {"field_key": "device_category", "option_value": "ELECTRIC_HOIST", "option_label": "电动葫芦", "sort_order": 30, "is_active": True},
            {"field_key": "work_order_type", "option_value": "MONTHLY_INSPECTION", "option_label": "月检", "sort_order": 10, "is_active": True},
            {"field_key": "work_order_type", "option_value": "QUARTERLY_INSPECTION", "option_label": "季检", "sort_order": 20, "is_active": True},
            {"field_key": "work_order_type", "option_value": "ANNUAL_INSPECTION", "option_label": "年检", "sort_order": 30, "is_active": True},
            {"field_key": "work_order_type", "option_value": "REPAIR", "option_label": "维修", "sort_order": 40, "is_active": True},
            {"field_key": "work_order_type", "option_value": "FIRST_INSPECTION", "option_label": "首次检验", "sort_order": 50, "is_active": True},
            {"field_key": "industry_type", "option_value": "STEEL_METALLURGY", "option_label": "钢铁冶金", "sort_order": 10, "is_active": True},
            {"field_key": "industry_type", "option_value": "EQUIPMENT_MANUFACTURING", "option_label": "装备制造", "sort_order": 20, "is_active": True},
            {"field_key": "industry_type", "option_value": "PORT_LOGISTICS", "option_label": "港口物流", "sort_order": 30, "is_active": True},
            {"field_key": "industry_type", "option_value": "POWER_ENERGY", "option_label": "电力能源", "sort_order": 40, "is_active": True},
            {"field_key": "industry_type", "option_value": "WAREHOUSING_LOGISTICS", "option_label": "仓储物流", "sort_order": 50, "is_active": True},
        ],
    )

    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _create_sqlite_updated_at_trigger("field_options")
    else:
        _create_mysql_updated_at_trigger("field_options")


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        _drop_sqlite_updated_at_trigger("field_options")
    else:
        _drop_mysql_updated_at_trigger("field_options")

    op.drop_index(op.f("ix_field_options_is_active"), table_name="field_options")
    op.drop_index(op.f("ix_field_options_field_key"), table_name="field_options")
    op.drop_table("field_options")
