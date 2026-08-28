import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import HTTPException

from app.database.session import SessionLocal
from app.schemas.auth import UserRegister
from app.services.auth import auth_service


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a local development user.",
    )
    parser.add_argument("email", help="Email address for the local user")
    parser.add_argument(
        "password",
        help="Password for the local user (minimum 8 characters)",
    )
    args = parser.parse_args()
    db = SessionLocal()

    try:
        user = auth_service.register_user(
            db,
            UserRegister(email=args.email, password=args.password),
        )
    except HTTPException as error:
        raise SystemExit(error.detail) from error
    finally:
        db.close()

    print(f"Development user created: {user.email}")


if __name__ == "__main__":
    main()
