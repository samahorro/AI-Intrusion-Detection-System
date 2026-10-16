from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User


def require_authenticated_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Require a valid authenticated backend session."""

    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    return user