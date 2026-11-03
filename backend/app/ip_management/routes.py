
"""KAN-230: Protected IP Management API Endpoints.

Provides authenticated endpoints for:
- Listing blocked IP addresses
- Permanently blocking IP addresses
- Unblocking IP addresses
- Enforcing user-specific record ownership

All firewall operations are simulated.
No real operating-system firewall rules are modified.
"""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.ip_management.permanent import block_permanently
from backend.app.ip_management.service import IPBlockingService
from backend.app.ip_management.unblocking import unblock_saved_ip
from backend.app.ip_management.validation import validate_ip_address
from backend.app.models.blocked_ip import BlockedIP
from backend.app.models.user import User

router = APIRouter(
    prefix="/blocked-ips",
    tags=["IP Management"],
)


# ==========================================================
# REQUEST MODELS
# ==========================================================

class BlockIPRequest(BaseModel):
    """Request body for permanently blocking an IP."""

    ip_address: str
    reason: str | None = Field(
        default=None,
        max_length=255,
    )


# ==========================================================
# AUTHENTICATION
# ==========================================================

def get_authenticated_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Get the authenticated user from the session."""

    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    return user


# ==========================================================
# IP BLOCKING SERVICE
# ==========================================================

def get_ip_service(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> IPBlockingService:
    """Create the simulated firewall service."""

    firewall = request.app.state.ip_firewall

    return IPBlockingService(
        db,
        firewall,
    )


# ==========================================================
# IP ADDRESS VALIDATION
# ==========================================================

def validate_ip(value: str) -> str:
    """Validate an IP address before processing."""

    try:
        return validate_ip_address(value)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ==========================================================
# RESPONSE SERIALIZATION
# ==========================================================

def serialize_record(
    record: BlockedIP,
) -> dict:
    """Convert a blocked IP record into JSON-compatible data."""

    return {
        "id": record.id,
        "ip_address": record.ip_address,
        "block_type": record.block_type,
        "reason": record.reason,
        "status": record.status,
        "created_by_user_id": record.created_by_user_id,
        "created_at": (
            record.created_at.isoformat()
            if record.created_at
            else None
        ),
        "expires_at": (
            record.expires_at.isoformat()
            if record.expires_at
            else None
        ),
    }


# ==========================================================
# GET /blocked-ips
# ==========================================================

@router.get("")
def list_blocked_ips(
    user: Annotated[User, Depends(get_authenticated_user)],
    service: Annotated[IPBlockingService, Depends(get_ip_service)],
):
    """List saved IP records owned by the current user."""

    records = (
        service.db.query(BlockedIP)
        .filter(
            BlockedIP.created_by_user_id == user.id
        )
        .order_by(
            BlockedIP.id.desc()
        )
        .all()
    )

    return {
        "items": [
            serialize_record(record)
            for record in records
        ],
        "total": len(records),
        "simulation_only": True,
    }


# ==========================================================
# POST /blocked-ips
# ==========================================================

@router.post("", status_code=201)
def create_block(
    payload: BlockIPRequest,
    user: Annotated[User, Depends(get_authenticated_user)],
    service: Annotated[IPBlockingService, Depends(get_ip_service)],
):
    """Create a permanent simulated block for the current user."""

    ip_address = validate_ip(
        payload.ip_address
    )

    # Check whether an IP record already exists.
    existing = service.get_record(
        ip_address
    )

    # Do not allow another user to overwrite an
    # existing blocked IP record.
    if (
        existing is not None
        and existing.created_by_user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="IP record not found.",
        )

    try:
        # Use the existing KAN-228 implementation.
        # Its actual signature accepts:
        # service, ip_address, and reason.
        result = block_permanently(
            service,
            ip_address,
            reason=payload.reason,
        )

        # Retrieve the saved database record.
        record = service.get_record(
            ip_address
        )

        if record is None:
            raise RuntimeError(
                "Blocked IP record was not saved."
            )

        # Associate the record with the
        # authenticated user.
        #
        # The existing blocking service does not
        # accept created_by_user_id directly.
        record.created_by_user_id = user.id

        service.db.commit()

    except ValueError as exc:
        service.db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (RuntimeError, SQLAlchemyError) as exc:
        service.db.rollback()

        raise HTTPException(
            status_code=503,
            detail="Unable to save simulated IP block.",
        ) from exc

    return asdict(result)


# ==========================================================
# DELETE /blocked-ips/{ip_address}
# ==========================================================

@router.delete("/{ip_address}")
def delete_block(
    ip_address: str,
    user: Annotated[User, Depends(get_authenticated_user)],
    service: Annotated[IPBlockingService, Depends(get_ip_service)],
):
    """Unblock a saved IP belonging to the current user."""

    normalized_ip = validate_ip(
        ip_address
    )

    # Find the existing record.
    existing = service.get_record(
        normalized_ip
    )

    # Reject records that do not exist or
    # belong to another authenticated user.
    if (
        existing is None
        or existing.created_by_user_id != user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="IP record not found.",
        )

    try:
        # Use the existing KAN-229
        # IP unblocking implementation.
        result = unblock_saved_ip(
            service,
            normalized_ip,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (RuntimeError, SQLAlchemyError) as exc:
        service.db.rollback()

        raise HTTPException(
            status_code=503,
            detail="Unable to unblock IP address.",
        ) from exc

    return asdict(result)
