import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .auth.routes import router as auth_router
from .database import init_db
from .detection.routes import router as detection_router


def create_app(
    initialize_database: bool = True,
):
    """Create the FastAPI application."""

    app = FastAPI(
        title="AI Intrusion Detection System API",
        version="0.3.0",
    )

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv(
            "SECRET_KEY",
            "development-only-change-me",
        ),
        same_site="lax",
        https_only=False,
    )

    app.include_router(auth_router)
    app.include_router(detection_router)

    @app.get("/health")
    def health():
        return {
            "status": "ok",
        }

    if initialize_database:
        init_db()

    return app


app = create_app()