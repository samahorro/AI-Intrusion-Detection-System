
"""Main FastAPI application for the AEGIS AI Intrusion Detection System."""

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
from .ip_management.firewall import SimulatedFirewall
from .ip_management.routes import router as ip_management_router


def create_app(initialize_database: bool = True):
    """Create and configure the AEGIS FastAPI application."""

    app = FastAPI(
        title="AI Intrusion Detection System API",
        version="0.3.0",
    )

    # ==================================================
    # PRODUCTION SECURITY CONFIGURATION
    # ==================================================

    production = (
        os.getenv("APP_ENV", "development").lower()
        == "production"
    )

    secret_key = os.getenv("SECRET_KEY", "")

    if production and (
        len(secret_key) < 32
        or secret_key == "development-only-change-me"
    ):
        raise RuntimeError(
            "Production requires a unique SECRET_KEY "
            "of at least 32 characters"
        )

    # ==================================================
    # KAN-230: SAFE SIMULATED FIREWALL
    # ==================================================

    # All IP blocking operations are simulated.
    # No operating-system firewall rules are modified.
    app.state.ip_firewall = SimulatedFirewall()

    # ==================================================
    # FRONTEND CORS CONFIGURATION
    # ==================================================

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )

    # Production requires a secure frontend origin.
    if production and not frontend_origin.startswith(
        "https://"
    ):
        raise RuntimeError(
            "Production FRONTEND_ORIGIN must use HTTPS"
        )

    # Production permits only the configured origin.
    # Development permits common local Vite ports.
    if production:
        allowed_origins = [frontend_origin]
    else:
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

    # Production cookies require HTTPS.
    # Development retains local HTTP compatibility.
    app.add_middleware(
        SessionMiddleware,
        secret_key=(
            secret_key or "development-only-change-me"
        ),
        same_site="lax",
        https_only=production,
        max_age=3600,
    )

    # ==================================================
    # SECURITY RESPONSE HEADERS
    # ==================================================

    @app.middleware("http")
    async def security_headers(request, call_next):
        """Add security-related HTTP response headers."""

        response = await call_next(request)

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        response.headers[
            "Referrer-Policy"
        ] = "no-referrer"

        response.headers[
            "Cache-Control"
        ] = "no-store"

        if production:
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000"

        return response

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
    # AUTHENTICATION ROUTES
    # ==================================================

    # /auth/register
    # /auth/login
    # /auth/me
    # /auth/logout
    app.include_router(auth_router)

    # ==================================================
    # INTRUSION DETECTION ROUTES
    # ==================================================

    app.include_router(detection_router)

    # ==================================================
    # NETWORK CAPTURE ROUTES
    # ==================================================

    app.include_router(capture_router)

    # ==================================================
    # KAN-230: PROTECTED IP MANAGEMENT ROUTES
    # ==================================================

    # GET    /blocked-ips
    # POST   /blocked-ips
    # DELETE /blocked-ips/{ip_address}
    #
    # Authentication and record ownership are enforced
    # in the IP management router.

    app.include_router(ip_management_router)

    # ==================================================
    # HEALTH CHECK
    # ==================================================

    @app.get("/health")
    def health():
        """Return application health status."""

        return {
            "status": "ok",
        }

    # ==================================================
    # DATABASE INITIALIZATION
    # ==================================================

    if initialize_database:
        init_db()

    return app


# Application used by Uvicorn and automated tests.
app = create_app()
