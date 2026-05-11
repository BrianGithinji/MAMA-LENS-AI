import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user


class DailyJournalEntry(BaseModel):
    mood: str = Field(..., description="Overall mood: great/good/okay/low/bad")
    energy_level: int = Field(..., ge=1, le=10, description="Energy level 1-10")
    symptoms: List[str] = Field(default=[], description="List of symptoms experienced")
    pain_level: Optional[int] = Field(None, ge=0, le=10, description="Pain level 0-10")
    sleep_hours: Optional[float] = Field(None, description="Hours of sleep")
    notes: Optional[str] = Field(None, max_length=1000, description="Free-text notes for doctor")
    concerns: Optional[str] = Field(None, max_length=500, description="Any concerns to flag for doctor")

router = APIRouter()


@router.get("/")
async def get_health_records(
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    cursor = db.health_records.find(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
        limit=limit,
    )
    records = await cursor.to_list(length=limit)
    return [{"id": r["_id"], "record_type": r["record_type"], "created_at": r["created_at"]} for r in records]


@router.post("/vitals", status_code=201)
async def log_vitals(
    vitals: dict,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    vital_id = str(uuid.uuid4())

    systolic = vitals.get("systolic_bp")
    diastolic = vitals.get("diastolic_bp")
    glucose = vitals.get("blood_glucose")

    is_hypertensive = bool(systolic and diastolic and (systolic >= 140 or diastolic >= 90))
    is_hypoglycemic = bool(glucose and glucose < 70)
    bp_display = f"{int(systolic)}/{int(diastolic)} mmHg" if systolic and diastolic else None

    doc = {
        "_id": vital_id,
        "user_id": current_user["_id"],
        "systolic_bp": systolic,
        "diastolic_bp": diastolic,
        "heart_rate": vitals.get("heart_rate"),
        "blood_glucose": glucose,
        "hemoglobin": vitals.get("hemoglobin"),
        "weight_kg": vitals.get("weight_kg"),
        "temperature": vitals.get("temperature"),
        "oxygen_saturation": vitals.get("oxygen_saturation"),
        "fetal_heart_rate": vitals.get("fetal_heart_rate"),
        "source": vitals.get("source", "manual"),
        "created_at": now,
    }
    await db.vital_signs.insert_one(doc)
    return {"id": vital_id, "is_hypertensive": is_hypertensive, "is_hypoglycemic": is_hypoglycemic, "bp_display": bp_display}


@router.get("/vitals")
async def get_vitals(
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    cursor = db.vital_signs.find(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
        limit=limit,
    )
    vitals = await cursor.to_list(length=limit)
    return [
        {
            "id": v["_id"],
            "bp": f"{int(v['systolic_bp'])}/{int(v['diastolic_bp'])} mmHg" if v.get("systolic_bp") and v.get("diastolic_bp") else None,
            "heart_rate": v.get("heart_rate"),
            "blood_glucose": v.get("blood_glucose"),
            "hemoglobin": v.get("hemoglobin"),
            "weight_kg": v.get("weight_kg"),
            "source": v.get("source"),
            "created_at": v["created_at"],
        }
        for v in vitals
    ]


@router.post("/daily-journal", status_code=201)
async def log_daily_journal(
    entry: DailyJournalEntry,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    entry_id = str(uuid.uuid4())
    doc = {
        "_id": entry_id,
        "user_id": current_user["_id"],
        "date": now[:10],  # YYYY-MM-DD for easy daily lookup
        "mood": entry.mood,
        "energy_level": entry.energy_level,
        "symptoms": entry.symptoms,
        "pain_level": entry.pain_level,
        "sleep_hours": entry.sleep_hours,
        "notes": entry.notes,
        "concerns": entry.concerns,
        "created_at": now,
    }
    await db.daily_journal.insert_one(doc)
    return {"id": entry_id, "date": doc["date"], "created_at": now}


@router.get("/daily-journal")
async def get_daily_journal(
    limit: int = Query(30, le=90),
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    cursor = db.daily_journal.find(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
        limit=limit,
    )
    entries = await cursor.to_list(length=limit)
    return [
        {
            "id": e["_id"],
            "date": e["date"],
            "mood": e["mood"],
            "energy_level": e["energy_level"],
            "symptoms": e.get("symptoms", []),
            "pain_level": e.get("pain_level"),
            "sleep_hours": e.get("sleep_hours"),
            "notes": e.get("notes"),
            "concerns": e.get("concerns"),
            "created_at": e["created_at"],
        }
        for e in entries
    ]
