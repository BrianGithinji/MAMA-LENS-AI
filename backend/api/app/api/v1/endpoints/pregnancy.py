import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


class CreatePregnancyRequest(BaseModel):
    status: str = "pregnant"
    last_menstrual_period: Optional[str] = None
    gestational_age_weeks: Optional[int] = None
    gravida: int = 1
    para: int = 0
    previous_miscarriages: int = 0
    pre_existing_conditions: list = []
    blood_type: Optional[str] = None
    grief_support_requested: bool = False


@router.post("/", status_code=201)
async def create_pregnancy_profile(
    request: CreatePregnancyRequest,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    await db.pregnancy_profiles.update_many(
        {"user_id": current_user["_id"], "is_active": True},
        {"$set": {"is_active": False}}
    )

    now = datetime.now(timezone.utc).isoformat()
    profile_id = str(uuid.uuid4())
    doc = {
        "_id": profile_id,
        "user_id": current_user["_id"],
        "status": request.status,
        "gestational_age_weeks": request.gestational_age_weeks,
        "last_menstrual_period": request.last_menstrual_period,
        "gravida": request.gravida,
        "para": request.para,
        "abortus": 0,
        "living_children": 0,
        "previous_miscarriages": request.previous_miscarriages,
        "pre_existing_conditions": request.pre_existing_conditions,
        "blood_type": request.blood_type,
        "grief_support_requested": request.grief_support_requested,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    await db.pregnancy_profiles.insert_one(doc)
    return {"id": profile_id, "status": request.status, "message": "Pregnancy profile created"}


@router.get("/active")
async def get_active_pregnancy(current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    profile = await db.pregnancy_profiles.find_one(
        {"user_id": current_user["_id"], "is_active": True}
    )
    if not profile:
        return {"message": "No active pregnancy profile found", "profile": None}
    return {
        "id": profile["_id"],
        "status": profile["status"],
        "gestational_age_weeks": profile.get("gestational_age_weeks"),
        "estimated_due_date": profile.get("estimated_due_date"),
        "obstetric_history": f"G{profile.get('gravida',1)}P{profile.get('para',0)}A{profile.get('abortus',0)}L{profile.get('living_children',0)}",
        "grief_support_requested": profile.get("grief_support_requested", False),
        "previous_miscarriages": profile.get("previous_miscarriages", 0),
    }


@router.get("/")
async def list_pregnancies(current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    cursor = db.pregnancy_profiles.find({"user_id": current_user["_id"]})
    profiles = await cursor.to_list(length=20)
    return [{"id": p["_id"], "status": p["status"], "gestational_age_weeks": p.get("gestational_age_weeks")} for p in profiles]
