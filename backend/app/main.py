import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .auth.routes import router as auth_router
from .database import init_db


def create_app(
    initialize_database: bool = True,
):
    """Create the FastAPI application."""

    app = FastAPI(
        title="AI Intrusion Detection System API",
        version="0.2.0",
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

    @app.get("/health")
    def health():
        return {
            "status": "ok",
        }

    if initialize_database:
        init_db()

    return app


app = create_app()