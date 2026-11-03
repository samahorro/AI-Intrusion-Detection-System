
import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .auth.routes import router as auth_router
from .capture.routes import router as capture_router
from .database import init_db
from .detection.routes import router as detection_router

# KAN-230: Protected IP management
from .ip_management.firewall import SimulatedFirewall
from .ip_management.routes import router as ip_management_router


def create_app(initialize_database: bool = True):
    """Create and configure the AEGIS FastAPI application."""

    app = FastAPI(
        title="AI Intrusion Detection System API",
        version="0.3.0",
    )

    # ==================================================
    # KAN-230: SAFE SIMULATED FIREWALL
    # ==================================================

    # Store the simulated firewall on the application.
    # No real operating-system firewall rules are changed.
    app.state.ip_firewall = SimulatedFirewall()

    # ==================================================
    # FRONTEND CORS CONFIGURATION
    # ==================================================

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )

    # Support common Vite development ports.
    allowed_origins = list(
        {
            frontend_origin,
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        }
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==================================================
    # SESSION AUTHENTICATION
    # ==================================================

    # Existing development configuration is preserved.
    # Production security improvements are tracked
    # separately under SOC 2 Validation 7.
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv(
            "SECRET_KEY",
            "development-only-change-me",
        ),
        same_site="lax",
        https_only=False,
    )

    # ==================================================
    # REQUEST VALIDATION ERROR HANDLING
    # ==================================================

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request,
        exc: RequestValidationError,
    ):
        """Return validation errors without exposing input."""

        safe_errors = []

        for error in exc.errors():
            safe_errors.append(
                {
                    "type": error.get("type"),
                    "loc": error.get("loc"),
                    "msg": error.get("msg"),
                }
            )

        return JSONResponse(
            status_code=422,
            content={
                "detail": safe_errors,
            },
        )

    # ==================================================
    # REGISTER BACKEND API ROUTERS
    # ==================================================

    # Authentication:
    # /auth/register
    # /auth/login
    # /auth/me
    # /auth/logout
    app.include_router(auth_router)

    # Intrusion detection endpoints
    app.include_router(detection_router)

    # Network capture and flow aggregation endpoints
    app.include_router(capture_router)

    # ==================================================
    # KAN-230: PROTECTED IP MANAGEMENT ENDPOINTS
    # ==================================================

    # GET    /blocked-ips
    # POST   /blocked-ips
    # DELETE /blocked-ips/{ip_address}
    #
    # Authentication and record ownership checks are
    # enforced by the IP management router.
    app.include_router(ip_management_router)

    # ==================================================
    # HEALTH CHECK ENDPOINT
    # ==================================================

    @app.get("/health")
    def health():
        """Return the backend health status."""

        return {
            "status": "ok",
        }

    # ==================================================
    # DATABASE INITIALIZATION
    # ==================================================

    if initialize_database:
        init_db()

    return app


# Application instance used by Uvicorn and tests.
app = create_app()
