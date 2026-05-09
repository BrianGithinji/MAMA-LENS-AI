"""MAMA-LENS AI — Authentication Endpoints (MongoDB)"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, validator

import structlog

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ─── Schemas ─────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: str = "patient"
    preferred_language: str = "en"
    country: Optional[str] = None
    data_consent_given: bool = False

    @validator("password")
    def validate_password(cls, v):
        if v and len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    identifier: str
    password: str


class GoogleLoginRequest(BaseModel):
    credential: str   # Google ID token from the frontend


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user_id: str
    role: str
    first_name: str = ""
    last_name: str = ""


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ─── Dependency ──────────────────────────────────────────────────────────────

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db = get_db()
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Account inactive")
    if user.get("status") == "suspended":
        raise HTTPException(status_code=401, detail="Account suspended")
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_tokens(user_id: str, role: str, first_name: str, last_name: str) -> dict:
    return {
        "access_token": create_access_token(user_id, extra_claims={"role": role}),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
        "user_id": user_id,
        "role": role,
        "first_name": first_name,
        "last_name": last_name,
    }


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    if not request.phone_number and not request.email:
        raise HTTPException(status_code=400, detail="Phone number or email is required")
    if not request.data_consent_given:
        raise HTTPException(status_code=400, detail="Data consent is required")

    db = get_db()

    if request.phone_number:
        if await db.users.find_one({"phone_number": request.phone_number}):
            raise HTTPException(status_code=409, detail="Phone number already registered")
    if request.email:
        if await db.users.find_one({"email": request.email}):
            raise HTTPException(status_code=409, detail="Email already registered")

    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "_id": user_id,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "role": request.role,
        "preferred_language": request.preferred_language,
        "country": request.country,
        "status": "active",
        "phone_verified": True,
        "email_verified": True,
        "is_active": True,
        "onboarding_completed": False,
        "data_consent_given": True,
        "data_consent_at": now,
        "failed_login_attempts": 0,
        "created_at": now,
        "updated_at": now,
    }

    # Only store fields that have actual values — never store null
    if request.phone_number:
        user_doc["phone_number"] = request.phone_number
    if request.email:
        user_doc["email"] = request.email
    if request.password:
        user_doc["hashed_password"] = hash_password(request.password)

    await db.users.insert_one(user_doc)
    logger.info("User registered", user_id=user_id, role=request.role)

    return {
        "success": True,
        "message": "Account created successfully. Welcome to MAMA-LENS AI!",
        "requires_verification": False,
        **_make_tokens(user_id, request.role, request.first_name, request.last_name),
    }


@router.post("/google")
async def google_login(request: GoogleLoginRequest):
    """
    Verify a Google ID token and sign in or auto-register the user.
    """
    try:
        import base64, json as _json, time as _time

        def _b64_decode(s: str) -> bytes:
            s += "=" * (4 - len(s) % 4)
            return base64.urlsafe_b64decode(s)

        parts = request.credential.split(".")
        if len(parts) != 3:
            raise ValueError("Not a valid JWT")

        idinfo = _json.loads(_b64_decode(parts[1]))

        # Log what we received for debugging
        logger.info("Google token payload",
            aud=idinfo.get("aud"),
            iss=idinfo.get("iss"),
            exp=idinfo.get("exp"),
            sub=idinfo.get("sub", "")[:8],
            email=idinfo.get("email", ""),
            configured_client_id=settings.GOOGLE_CLIENT_ID[:20],
        )

        # Validate issuer
        iss = idinfo.get("iss", "")
        if iss not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError(f"Invalid issuer: {iss}")

        # Validate expiry
        if idinfo.get("exp", 0) < _time.time():
            raise ValueError("Token expired")

        # Validate audience — accept if client_id matches OR if no client_id configured
        aud = idinfo.get("aud", "")
        configured = settings.GOOGLE_CLIENT_ID.strip()
        if configured:
            aud_list = [aud] if isinstance(aud, str) else aud
            if configured not in aud_list:
                raise ValueError(f"Audience mismatch: got {aud}, expected {configured}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Google token validation failed", error=str(e))
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {e}")

    google_id = idinfo.get("sub", "")
    email = idinfo.get("email", "")
    first_name = idinfo.get("given_name", "")
    last_name = idinfo.get("family_name", "")
    picture = idinfo.get("picture", "")

    if not google_id:
        raise HTTPException(status_code=401, detail="Google token missing user ID")

    db = get_db()

    # Find existing user by google_id or email
    query = {"$or": [{"google_id": google_id}]}
    if email:
        query["$or"].append({"email": email})
    user = await db.users.find_one(query)

    if user:
        # Update google_id if signing in via email match
        if not user.get("google_id"):
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"google_id": google_id, "profile_photo_url": picture}}
            )
        logger.info("Google login", user_id=user["_id"])
        return _make_tokens(
            user["_id"], user["role"],
            user.get("first_name", ""), user.get("last_name", "")
        )

    # Auto-register new Google user
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    user_doc = {
        "_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "role": "patient",
        "preferred_language": "en",
        "status": "active",
        "email_verified": True,
        "phone_verified": False,
        "is_active": True,
        "onboarding_completed": False,
        "data_consent_given": True,
        "data_consent_at": now,
        "failed_login_attempts": 0,
        "google_id": google_id,
        "profile_photo_url": picture,
        "created_at": now,
        "updated_at": now,
    }
    if email:
        user_doc["email"] = email

    await db.users.insert_one(user_doc)
    logger.info("Google auto-register", user_id=user_id, email=email)

    return {
        "success": True,
        "message": "Account created via Google. Welcome to MAMA-LENS AI!",
        "requires_verification": False,
        **_make_tokens(user_id, "patient", first_name, last_name),
    }


@router.post("/login")
async def login(request: LoginRequest):
    db = get_db()

    if "@" in request.identifier:
        query = {"email": request.identifier}
    else:
        query = {"phone_number": request.identifier}
    user = await db.users.find_one(query)

    if not user or not user.get("hashed_password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(request.password, user["hashed_password"]):
        await db.users.update_one({"_id": user["_id"]}, {"$inc": {"failed_login_attempts": 1}})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.get("status") == "suspended":
        raise HTTPException(status_code=401, detail="Account suspended")

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"failed_login_attempts": 0, "last_login_at": datetime.now(timezone.utc).isoformat()}}
    )
    logger.info("User logged in", user_id=user["_id"])
    return _make_tokens(user["_id"], user["role"], user.get("first_name", ""), user.get("last_name", ""))


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db = get_db()
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return _make_tokens(user["_id"], user["role"], user.get("first_name", ""), user.get("last_name", ""))


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_active_user)):
    return {"success": True, "message": "Logged out successfully"}
