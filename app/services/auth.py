from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.auth import UserRegister


class AuthService:

    def register_user(
        self,
        db: Session,
        user_data: UserRegister,
    ) -> User:
        if user_repository.get_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )

        return user_repository.create(db, user)

    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str,
    ) -> User:
        user = user_repository.get_by_email(db, email)

        if (
            not user
            or not user.is_active
            or not verify_password(password, user.hashed_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    def create_token_for_user(self, user: User) -> str:
        return create_access_token(user.id)


auth_service = AuthService()
