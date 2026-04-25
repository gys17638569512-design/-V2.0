"""M02 quality fixes for constraints and timestamp triggers.

Revision ID: 202604250002
Revises: 202604250001
Create Date: 2026-04-25 00:20:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "202604250002"
down_revision: str | None = "202604250001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

ROLE_VALUES = (
    "SUPER_ADMIN",
    "ADMIN",
    "MANAGER",
    "TECH",
    "CLIENT",
    "DEALER",
)
ROLE_CHECK_SQL = "role IN ({})".format(", ".join(f"'{role}'" for role in ROLE_VALUES))


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
    dialect_name = op.get_bind().dialect.name

    if dialect_name == "sqlite":
        with op.batch_alter_table("users", recreate="always") as batch_op:
            batch_op.create_check_constraint(op.f("ck_users_user_role"), ROLE_CHECK_SQL)
        _create_sqlite_updated_at_trigger("users")
        _create_sqlite_updated_at_trigger("customers")
    else:
        op.create_check_constraint(op.f("ck_users_user_role"), "users", ROLE_CHECK_SQL)
        _create_mysql_updated_at_trigger("users")
        _create_mysql_updated_at_trigger("customers")


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name

    if dialect_name == "sqlite":
        _drop_sqlite_updated_at_trigger("customers")
        _drop_sqlite_updated_at_trigger("users")
        with op.batch_alter_table("users", recreate="always") as batch_op:
            batch_op.drop_constraint(op.f("ck_users_user_role"), type_="check")
    else:
        _drop_mysql_updated_at_trigger("customers")
        _drop_mysql_updated_at_trigger("users")
        op.drop_constraint(op.f("ck_users_user_role"), "users", type_="check")
