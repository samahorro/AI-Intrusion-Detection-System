from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from .capture_service import capture_service

router = APIRouter(
    prefix="/capture",
    tags=["capture"],
)


class CaptureStartRequest(BaseModel):
    """Request body used to start packet capture."""

    interface: str = Field(
        min_length=1,
    )


@router.post("/start")
def start_capture(
    request: CaptureStartRequest,
):
    """Start packet capture on a selected interface."""

    if capture_service.is_running():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Packet capture is already running",
        )

    try:
        return capture_service.start(
            request.interface
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.post("/stop")
def stop_capture():
    """Stop the active packet capture."""

    if not capture_service.is_running():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Packet capture is not running",
        )

    try:
        return capture_service.stop()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/status")
def capture_status():
    """Return the current packet capture state."""

    running = capture_service.is_running()

    return {
        "status": (
            "running"
            if running
            else "stopped"
        ),
        "interface": (
            capture_service.interface
            if running
            else None
        ),
    }