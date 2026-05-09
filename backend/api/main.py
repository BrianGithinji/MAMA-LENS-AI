"""
MAMA-LENS AI — FastAPI Application Entry Point
MongoDB + Motor backend
"""
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.router import api_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    logger.info("Starting MAMA-LENS AI", version=settings.APP_VERSION, env=settings.APP_ENV)
    await init_db()

    # Seed demo facilities if collection is empty
    from app.core.seeder import seed_if_empty
    await seed_if_empty()

    logger.info("MAMA-LENS AI ready", url="http://localhost:8001")
    yield

    # ── Shutdown ─────────────────────────────────────────────
    await close_db()
    logger.info("MAMA-LENS AI shut down")


app = FastAPI(
    title="MAMA-LENS AI",
    description="Maternal Assessment & Monitoring for Early Loss Support",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Middleware ───────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        import traceback
        logger.error("Unhandled exception", error=str(exc), traceback=traceback.format_exc())
        raise
    response.headers["X-Response-Time"] = f"{round((time.time()-start)*1000,2)}ms"
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "INTERNAL_SERVER_ERROR", "message": str(exc), "detail": traceback.format_exc()},
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "MAMA-LENS AI",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "MongoDB Atlas",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to MAMA-LENS AI",
        "tagline": "Guiding Safer Pregnancies Through AI and Care",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
