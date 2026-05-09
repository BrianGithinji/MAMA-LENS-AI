"""MAMA-LENS AI — Telemedicine Endpoints (MongoDB)"""
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.endpoints.auth import get_current_active_user

logger = structlog.get_logger(__name__)
router = APIRouter()


class CreateConsultationRequest(BaseModel):
    appointment_id: Optional[str] = None
    consultation_type: str = "video"
    chief_complaint: Optional[str] = None
    recording_consent: bool = False


class ConsultationNotesRequest(BaseModel):
    clinical_notes: Optional[str] = None
    diagnoses: Optional[list] = None
    prescriptions: Optional[list] = None
    follow_up_instructions: Optional[str] = None
    follow_up_date: Optional[str] = None


class ConsultationFeedbackRequest(BaseModel):
    rating: int
    feedback: Optional[str] = None
    connection_quality: Optional[str] = None


def _generate_livekit_token(room_name: str, identity: str, name: str, is_clinician: bool = False) -> str:
    try:
        from livekit import api as lk  # type: ignore
        token = lk.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        token.with_identity(identity).with_name(name)
        token.with_grants(lk.VideoGrants(room_join=True, room=room_name, can_publish=True, can_subscribe=True))
        return token.to_jwt()
    except Exception:
        return f"dev_token_{secrets.token_urlsafe(24)}"


@router.post("/start", status_code=201)
async def start_consultation(
    request: CreateConsultationRequest,
    current_user: dict = Depends(get_current_active_user),
):
    room_name = f"mamalens_{secrets.token_urlsafe(12)}"
    full_name = f"{current_user['first_name']} {current_user['last_name']}"
    is_hw = current_user.get("role") in ["doctor", "midwife", "specialist", "community_health_worker"]
    token = _generate_livekit_token(room_name, current_user["_id"], full_name, is_hw)

    now = datetime.now(timezone.utc).isoformat()
    consultation_id = str(uuid.uuid4())
    doc = {
        "_id": consultation_id,
        "appointment_id": request.appointment_id,
        "patient_id": current_user["_id"],
        "status": "waiting",
        "consultation_type": request.consultation_type,
        "livekit_room_name": room_name,
        "livekit_room_token": token,
        "chief_complaint": request.chief_complaint,
        "recording_consent_given": request.recording_consent,
        "started_at": now,
        "created_at": now,
    }
    db = get_db()
    await db.consultations.insert_one(doc)

    logger.info("Consultation started", id=consultation_id, room=room_name)
    return {
        "consultation_id": consultation_id,
        "room_name": room_name,
        "token": token,
        "livekit_url": settings.LIVEKIT_URL,
        "consultation_type": request.consultation_type,
        "status": "waiting",
    }


@router.post("/{consultation_id}/join")
async def join_consultation(
    consultation_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    c = await db.consultations.find_one({"_id": consultation_id})
    if not c:
        raise HTTPException(status_code=404, detail="Consultation not found")
    if c["patient_id"] != current_user["_id"] and c.get("clinician_id") != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    full_name = f"{current_user['first_name']} {current_user['last_name']}"
    is_hw = current_user.get("role") in ["doctor", "midwife", "specialist", "community_health_worker"]
    token = _generate_livekit_token(c["livekit_room_name"], current_user["_id"], full_name, is_hw)

    now = datetime.now(timezone.utc).isoformat()
    update: dict = {}
    if is_hw and not c.get("clinician_joined_at"):
        update = {"clinician_joined_at": now, "status": "in_progress", "clinician_id": current_user["_id"]}
    elif not c.get("patient_joined_at"):
        update = {"patient_joined_at": now}
    if update:
        await db.consultations.update_one({"_id": consultation_id}, {"$set": update})

    return {"consultation_id": c["_id"], "room_name": c["livekit_room_name"], "token": token, "livekit_url": settings.LIVEKIT_URL, "status": c["status"]}


@router.post("/{consultation_id}/end")
async def end_consultation(
    consultation_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    c = await db.consultations.find_one({"_id": consultation_id})
    if not c:
        raise HTTPException(status_code=404, detail="Consultation not found")

    now = datetime.now(timezone.utc)
    duration = None
    if c.get("started_at"):
        try:
            started = datetime.fromisoformat(c["started_at"])
            duration = int((now - started).total_seconds())
        except Exception:
            pass

    await db.consultations.update_one(
        {"_id": consultation_id},
        {"$set": {"status": "completed", "ended_at": now.isoformat(), "duration_seconds": duration}}
    )
    return {"success": True, "consultation_id": consultation_id, "duration_seconds": duration}


@router.put("/{consultation_id}/notes")
async def update_notes(
    consultation_id: str,
    request: ConsultationNotesRequest,
    current_user: dict = Depends(get_current_active_user),
):
    is_hw = current_user.get("role") in ["doctor", "midwife", "specialist", "community_health_worker"]
    if not is_hw:
        raise HTTPException(status_code=403, detail="Only healthcare workers can add clinical notes")
    db = get_db()
    await db.consultations.update_one(
        {"_id": consultation_id},
        {"$set": {
            "clinical_notes": request.clinical_notes,
            "follow_up_instructions": request.follow_up_instructions,
            "follow_up_date": request.follow_up_date,
        }}
    )
    return {"success": True}


@router.post("/{consultation_id}/feedback")
async def submit_feedback(
    consultation_id: str,
    request: ConsultationFeedbackRequest,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    c = await db.consultations.find_one({"_id": consultation_id})
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    if c["patient_id"] == current_user["_id"]:
        await db.consultations.update_one(
            {"_id": consultation_id},
            {"$set": {"patient_rating": request.rating, "patient_feedback": request.feedback, "connection_quality": request.connection_quality}}
        )
    return {"success": True, "message": "Feedback submitted. Thank you!"}


@router.get("/history")
async def get_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    cursor = db.consultations.find(
        {"$or": [{"patient_id": current_user["_id"]}, {"clinician_id": current_user["_id"]}]},
        sort=[("created_at", -1)],
        limit=limit,
    )
    consultations = await cursor.to_list(length=limit)
    return [{"id": c["_id"], "status": c["status"], "type": c["consultation_type"], "duration_seconds": c.get("duration_seconds"), "started_at": c.get("started_at")} for c in consultations]
