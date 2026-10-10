from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .capture_service import capture_service
from .interface_service import list_capture_interfaces

router = APIRouter(prefix="/capture", tags=["capture"])


class StartCaptureRequest(BaseModel):
    interface: str


@router.get("/interfaces")
def get_interfaces():
    try:
        return {"interfaces": list_capture_interfaces()}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/status")
def get_status():
    return {"running": capture_service.is_running(),
            "interface": capture_service.interface if capture_service.is_running() else None}


@router.get("/stats")
def get_stats():
    return capture_service.get_stats()


@router.get("/flows")
def get_flow_preview():
    return capture_service.flow_bridge.snapshot()


@router.post("/start")
def start_capture(request: StartCaptureRequest):
    try:
        return capture_service.start(request.interface)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/stop")
def stop_capture():
    try:
        return capture_service.stop()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
