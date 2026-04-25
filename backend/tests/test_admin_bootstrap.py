from app.bootstrap_admin import main
from app.db.session import get_session_factory
from app.models import User


def test_bootstrap_admin_command_creates_initial_admin(auth_client) -> None:
    exit_code = main(
        [
            "--username",
            "root-admin",
            "--password",
            "StrongPass123!",
            "--full-name",
            "初始管理员",
        ]
    )

    assert exit_code == 0

    session = get_session_factory()()
    try:
        user = session.query(User).filter(User.username == "root-admin").one()
        assert user.full_name == "初始管理员"
        assert user.role.value == "ADMIN"
        assert user.is_active is True
    finally:
        session.close()


def test_bootstrap_admin_command_rejects_second_initial_admin(auth_client) -> None:
    first_exit_code = main(
        [
            "--username",
            "root-admin",
            "--password",
            "StrongPass123!",
            "--full-name",
            "初始管理员",
        ]
    )
    second_exit_code = main(
        [
            "--username",
            "another-admin",
            "--password",
            "StrongPass456!",
            "--full-name",
            "第二管理员",
        ]
    )

    assert first_exit_code == 0
    assert second_exit_code == 1

    session = get_session_factory()()
    try:
        users = session.query(User).all()
        assert len(users) == 1
        assert users[0].username == "root-admin"
    finally:
        session.close()
