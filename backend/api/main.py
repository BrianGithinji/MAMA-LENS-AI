from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router

logger = structlog.get_logger(__name__)

_db_ready = False


async def _preload_model():
    """No-op: HF Inference API is called on demand per request."""
    logger.info("AI engine ready (HF Inference API, on-demand)")


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
    # Preload the fine-tuned model in background so first chat request is fast
    asyncio.create_task(_preload_model())
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

# Merge hardcoded production origins with any set via ALLOWED_ORIGINS env var
_base_origins = [
    "https://mama-lens.netlify.app",
    "https://mama-lens-ai.netlify.app",
    "https://mama-lens-ai.onrender.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
origins = list(set(_base_origins + settings.ALLOWED_ORIGINS))

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
    ai_model_status = "unavailable"
    ai_model_path = None
    try:
        from app.api.v1.endpoints.ai_avatar import _ai, _AI_AVAILABLE
        if _AI_AVAILABLE and _ai is not None:
            available = _ai._check_local_model()
            ai_model_status = "local_model" if available else "rule_based_fallback"
            import sys
            for p in sys.path:
                if "mama_model" in p:
                    ai_model_path = p
                    break
    except Exception as e:
        ai_model_status = f"error: {str(e)[:80]}"

    return {
        "status": "healthy",
        "service": "MAMA-LENS AI",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "MongoDB Atlas",
        "db_ready": _db_ready,
        "ai_model": ai_model_status,
        "ai_model_path": ai_model_path,
    }


@app.get("/debug/network")
async def debug_network():
    """Test outbound connectivity from Render to HuggingFace."""
    import httpx, os
    hf_token = os.environ.get("HF_API_TOKEN", "")
    results = {}
    for url in [
        "https://huggingface.co",
        "https://api-inference.huggingface.co",
        "https://router.huggingface.co",
        f"https://router.huggingface.co/hf-inference/models/BrianGithinji/mama-flan-t5/v1/text-generation",
    ]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(url, headers={"Authorization": f"Bearer {hf_token}"} if hf_token else {})
                results[url] = {"status": r.status_code}
        except Exception as e:
            results[url] = {"error": str(e)}
    return results


@app.get("/debug/ai")
async def debug_ai():
    import os, sys
    hf_model_id = os.environ.get("HF_MODEL_ID", "NOT SET").strip()
    hf_home = os.environ.get("HF_HOME", "/tmp/hf_cache")

    # List HF cache contents (shows whether model was pre-downloaded)
    hf_cache_files = []
    for root, dirs, files in os.walk(hf_home):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), hf_home)
            hf_cache_files.append(rel)
    hf_cache_files = hf_cache_files[:30]  # cap output

    try:
        import transformers
        transformers_ok = transformers.__version__
    except ImportError as e:
        transformers_ok = f"MISSING: {e}"

    try:
        import torch
        torch_ok = torch.__version__
    except ImportError as e:
        torch_ok = f"MISSING: {e}"

    # Check if model is actually loaded in memory
    model_loaded = False
    model_dtype = None
    try:
        from app.api.v1.endpoints.ai_avatar import _ai, _AI_AVAILABLE
        if _AI_AVAILABLE and _ai is not None and hasattr(_ai, "_hf_model") and _ai._hf_model is not None:
            model_loaded = True
            model_dtype = str(next(_ai._hf_model.parameters()).dtype)
    except Exception as e:
        model_loaded = f"error: {str(e)[:80]}"

    return {
        "HF_MODEL_ID": hf_model_id,
        "HF_HOME": hf_home,
        "hf_cache_file_count": len(hf_cache_files),
        "hf_cache_files": hf_cache_files,
        "model_loaded_in_memory": model_loaded,
        "model_dtype": model_dtype,
        "transformers": transformers_ok,
        "torch": torch_ok,
        "cwd": os.getcwd(),
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to MAMA-LENS AI",
        "tagline": "Guiding Safer Pregnancies Through AI and Care",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
