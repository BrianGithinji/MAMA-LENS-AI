"""
MAMA-LENS AI — FastAPI Application Entry Point
MongoDB + Motor backend

Port binds IMMEDIATELY so Render detects it.
MongoDB connects lazily on first request — startup never blocks.
"""
import os
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router

logger = structlog.get_logger(__name__)

# Track whether DB has been initialised
_db_ready = False


async def _ensure_db():
    """Initialise DB indexes and seed data on first use."""
    global _db_ready
    if _db_ready:
        return
    try:
        from app.core.database import init_db
        from app.core.seeder import seed_if_empty
        await init_db()
        await seed_if_empty()
        _db_ready = True
        logger.info("MongoDB ready")
    except Exception as e:
        logger.error("MongoDB init failed", error=str(e))
        # Don't crash — let health check report degraded state


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup — bind port immediately, DB connects lazily ──
    logger.info("MAMA-LENS AI starting", version=settings.APP_VERSION, env=settings.APP_ENV)
    # Kick off DB init in background so port binds without waiting
    import asyncio
    asyncio.create_task(_ensure_db())
    yield
    # ── Shutdown ─────────────────────────────────────────────
    try:
        from app.core.database import close_db
        await close_db()
    except Exception:
        pass
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
    allow_origins=[
        "https://mama-lens.netlify.app",
        "https://mama-lens-ai.netlify.app",
        "https://mamalens.netlify.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
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
        content={"success": False, "error": "INTERNAL_SERVER_ERROR", "message": str(exc)},
    )

# ─── Routes ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    """Handle CORS preflight OPTIONS requests explicitly."""
    from fastapi.responses import Response
    response = Response()
    origin = request.headers.get("origin", "")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


@app.get("/health", tags=["System"])
async def health_check():
    """Health check — always responds immediately."""
    return {
        "status": "healthy",
        "service": "MAMA-LENS AI",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "MongoDB Atlas",
        "db_ready": _db_ready,
        "cors": "all origins allowed" if settings.APP_ENV == "production" else "restricted",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to MAMA-LENS AI",
        "tagline": "Guiding Safer Pregnancies Through AI and Care",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
