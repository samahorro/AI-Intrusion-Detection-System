
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


def create_app(initialize_database: bool = True):
    """
    Create the AEGIS FastAPI application.

    Includes:
    - Authentication and session management
    - CORS configuration for the React frontend
    - Live TShark network capture endpoints
    - Experimental AI intrusion detection endpoints
    - Request validation and database initialization
    """

    app = FastAPI(
        title="AI Intrusion Detection System API",
        version="0.3.0",
    )

    production = os.getenv("APP_ENV", "development").lower() == "production"
    secret_key = os.getenv("SECRET_KEY", "")
    if production and (len(secret_key) < 32 or secret_key == "development-only-change-me"):
        raise RuntimeError("Production requires a unique SECRET_KEY of at least 32 characters")

    # ==================================================
    # FRONTEND CORS CONFIGURATION
    # ==================================================

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )

    # Support both common Vite development ports.
    # FRONTEND_ORIGIN allows an additional configured origin.
    if production and not frontend_origin.startswith("https://"):
        raise RuntimeError("Production FRONTEND_ORIGIN must use HTTPS")

    allowed_origins = [frontend_origin] if production else list({
        frontend_origin,
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    })

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

    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key or "development-only-change-me",
        same_site="lax",
        https_only=production,
    )

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        if production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    # ==================================================
    # REQUEST VALIDATION ERROR HANDLING
    # ==================================================

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request,
        exc: RequestValidationError,
    ):
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

    # User authentication and session endpoints
    app.include_router(auth_router)

    # Intrusion detection endpoints
    app.include_router(detection_router)

    # TShark network capture, flow aggregation,
    # and experimental Random Forest predictions
    app.include_router(capture_router)

    # ==================================================
    # HEALTH CHECK ENDPOINT
    # ==================================================

    @app.get("/health")
    def health():
        return {
            "status": "ok",
        }

    # ==================================================
    # DATABASE INITIALIZATION
    # ==================================================

    if initialize_database:
        init_db()

    return app


app = create_app()
