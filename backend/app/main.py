from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router
from app.core.config import settings
from app.db.database import engine, Base
from app.orchestrator.scheduler import scheduler, setup_scheduler
from app.services.scraper import scraper_factory

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("starting_regwatch", environment=settings.environment)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    setup_scheduler()
    if settings.environment == "production" and not scheduler.running:
        scheduler.start()
        logger.info("scheduler_started")

    yield

    if scheduler.running:
        scheduler.shutdown(wait=False)
    await scraper_factory.close()
    await engine.dispose()
    logger.info("regwatch_shutdown_complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": request.url.path},
    )
