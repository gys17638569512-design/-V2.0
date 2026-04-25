import argparse

from app.db.session import get_session_factory
from app.services.admin_bootstrap_service import AdminBootstrapService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize the first DMMS admin account.")
    parser.add_argument("--username", required=True, help="Initial admin username")
    parser.add_argument("--password", required=True, help="Initial admin password")
    parser.add_argument("--full-name", required=True, help="Initial admin display name")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    session = get_session_factory()()

    try:
        user = AdminBootstrapService(session).create_initial_admin(
            username=args.username,
            password=args.password,
            full_name=args.full_name,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    finally:
        session.close()

    print(f"Initial admin created: {user.username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
