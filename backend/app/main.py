"""Application entrypoint for the FastAPI backend."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.routers import health
from app.core.config import settings
from app.jobs.scheduler import start_scheduler, stop_scheduler
from app.utils.logging import (
    generate_request_id,
    get_app_logger,
    log_event,
    reset_request_id,
    set_request_id,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Run application startup and shutdown hooks for background jobs."""

    start_scheduler()
    try:
        yield
    finally:
        stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)
logger = get_app_logger(__name__)
REQUEST_ID_HEADER = "X-Request-ID"

if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_request_context(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach a request identifier, response header, and completion log to each request."""

    request_id = request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
    token = set_request_id(request_id)
    request.state.request_id = request_id
    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        log_event(
            logger,
            "app.request.completed",
            method=request.method,
            path=request.url.path,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            duration_ms=duration_ms,
            client_host=request.client.host if request.client else "unknown",
        )
        reset_request_id(token)
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    log_event(
        logger,
        "app.request.completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        client_host=request.client.host if request.client else "unknown",
    )
    reset_request_id(token)

    response.headers[REQUEST_ID_HEADER] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Log request validation failures with request context and preserve FastAPI semantics."""

    log_event(
        logger,
        "app.request.validation_failed",
        method=request.method,
        path=request.url.path,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_count=len(exc.errors()),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers={REQUEST_ID_HEADER: getattr(request.state, "request_id", generate_request_id())},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unhandled exceptions and return a generic internal-server-error response."""

    logger.exception(
        "app.unhandled_exception | method=%s path=%s request_id=%s",
        request.method,
        request.url.path,
        getattr(request.state, "request_id", "unknown"),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."},
        headers={REQUEST_ID_HEADER: getattr(request.state, "request_id", generate_request_id())},
    )


if settings.azure_demo_mode:
    app.include_router(health.router, prefix=f"{settings.api_v1_prefix}/health", tags=["health"])
else:
    app.include_router(api_router, prefix=settings.api_v1_prefix)
log_event(
    logger,
    "app.started",
    app_name=settings.app_name,
    environment=settings.environment,
    version=settings.app_version,
)
