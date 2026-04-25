import time
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_engine, reset_db_state
from app.models import Customer, FieldOption, User


def _reset_settings_state() -> None:
    get_settings.cache_clear()
    reset_db_state()


def _build_alembic_config() -> Config:
    alembic_ini_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    return Config(str(alembic_ini_path))


def test_minimum_foundation_models_are_registered() -> None:
    table_names = set(Base.metadata.tables)

    assert User.__tablename__ == "users"
    assert Customer.__tablename__ == "customers"
    assert FieldOption.__tablename__ == "field_options"
    assert {"users", "customers", "field_options"} <= table_names

    user_columns = set(Base.metadata.tables["users"].columns.keys())
    customer_columns = set(Base.metadata.tables["customers"].columns.keys())
    field_option_columns = set(Base.metadata.tables["field_options"].columns.keys())

    assert {
        "id",
        "username",
        "password_hash",
        "full_name",
        "role",
        "is_active",
        "token_version",
        "created_at",
        "updated_at",
    } <= user_columns
    assert {
        "id",
        "name",
        "manager_id",
        "is_active",
        "created_at",
        "updated_at",
    } <= customer_columns
    assert {
        "id",
        "field_key",
        "option_value",
        "option_label",
        "sort_order",
        "is_active",
        "created_at",
        "updated_at",
    } <= field_option_columns

    manager_fk_targets = {
        foreign_key.target_fullname
        for foreign_key in Base.metadata.tables["customers"].columns["manager_id"].foreign_keys
    }
    assert manager_fk_targets == {"users.id"}
    role_constraints = {
        str(constraint.sqltext)
        for constraint in Base.metadata.tables["users"].constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }
    assert any("role" in constraint for constraint in role_constraints)


def test_alembic_upgrade_accepts_percent_encoded_database_url(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "m02%25foundation.db"
    database_url = f"sqlite:///{database_path}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    _reset_settings_state()

    command.upgrade(_build_alembic_config(), "head")

    engine = get_engine()
    inspector = inspect(engine)
    assert {"users", "customers", "field_options"} <= set(inspector.get_table_names())

    _reset_settings_state()


def test_alembic_upgrade_enforces_role_constraint_and_foreign_keys(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "m02_foundation.db"
    database_url = f"sqlite:///{database_path}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    _reset_settings_state()
    command.upgrade(_build_alembic_config(), "head")

    engine = get_engine()
    users_table = Base.metadata.tables["users"]
    customers_table = Base.metadata.tables["customers"]

    with engine.begin() as connection:
        connection.execute(
            users_table.insert().values(
                username="manager",
                password_hash="hashed",
                full_name="Manager User",
                role="MANAGER",
                is_active=True,
            )
        )

        with pytest.raises(IntegrityError):
            connection.exec_driver_sql(
                """
                INSERT INTO users (username, password_hash, full_name, role, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("bad-role", "hashed", "Invalid Role", "NOT_A_ROLE", 1),
            )

        with pytest.raises(IntegrityError):
            connection.execute(
                customers_table.insert().values(
                    name="Broken FK Customer",
                    manager_id=9999,
                    is_active=True,
                )
            )

    _reset_settings_state()


def test_raw_database_update_refreshes_updated_at(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "m02_updated_at.db"
    database_url = f"sqlite:///{database_path}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    _reset_settings_state()
    command.upgrade(_build_alembic_config(), "head")

    engine = get_engine()
    users_table = Base.metadata.tables["users"]

    with engine.begin() as connection:
        insert_result = connection.execute(
            users_table.insert().values(
                username="updatable-user",
                password_hash="hashed",
                full_name="Before Update",
                role="ADMIN",
                is_active=True,
            )
        )
        user_id = insert_result.inserted_primary_key[0]
        before_update = connection.execute(
            select(users_table.c.updated_at).where(users_table.c.id == user_id)
        ).scalar_one()

    time.sleep(1.1)

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE users SET full_name = ? WHERE id = ?",
            ("After Update", user_id),
        )
        after_update = connection.execute(
            select(users_table.c.updated_at).where(users_table.c.id == user_id)
        ).scalar_one()

    assert after_update > before_update

    _reset_settings_state()
