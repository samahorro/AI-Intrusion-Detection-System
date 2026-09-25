from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from .validation import (
    hash_password,
    validate_password,
    validate_username,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user."""

    username = data.username.strip()

    username_valid, username_error = (
        validate_username(username)
    )

    if not username_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=username_error,
        )

    password_valid, password_error = (
        validate_password(data.password)
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error,
        )

    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    user = User(
        username=username,
        password_hash=hash_password(
            data.password
        ),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    return {
        "message": "User registered successfully.",
        "user": user.to_dict(),
    }


@router.post("/login")
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate an existing user."""

    username = data.username.strip()

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    # Return the same error for an invalid username
    # and an invalid password.
    if (
        user is None
        or not verify_password(
            data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    request.session.clear()

    request.session["user_id"] = user.id
    request.session["username"] = user.username

    return {
        "message": "Login successful.",
        "user": user.to_dict(),
    }


@router.post("/logout")
def logout(request: Request):
    """Clear the authenticated session."""

    request.session.clear()

    return {
        "message": "Logout successful.",
    }