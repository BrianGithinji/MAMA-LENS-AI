import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router

logger = structlog.get_logger(__name__)

_db_ready = False


async def _ensure_db():
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MAMA-LENS AI starting", version=settings.APP_VERSION)
    import asyncio
    asyncio.create_task(_ensure_db())
    yield
    try:
        from app.core.database import close_db
        await close_db()
    except Exception:
        pass


app = FastAPI(
    title="MAMA-LENS AI",
    description="Maternal Assessment & Monitoring for Early Loss Support",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

origins = [
    "https://mama-lens.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_coop_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "INTERNAL_SERVER_ERROR", "message": str(exc)},
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MAMA-LENS AI",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "MongoDB Atlas",
        "db_ready": _db_ready,
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to MAMA-LENS AI",
        "tagline": "Guiding Safer Pregnancies Through AI and Care",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
