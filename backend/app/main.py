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

    app.include_router(auth_router)
    app.include_router(detection_router)
    app.include_router(capture_router)

    @app.get("/health")
    def health():
        return {
            "status": "ok",
        }

    if initialize_database:
        init_db()

    return app


app = create_app()