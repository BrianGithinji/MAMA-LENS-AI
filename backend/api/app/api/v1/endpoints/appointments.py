import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


class CreateAppointmentRequest(BaseModel):
    appointment_type: str = "antenatal_care"
    scheduled_at: str
    duration_minutes: int = 30
    is_telemedicine: bool = False
    reason: Optional[str] = None
    priority: str = "routine"


@router.get("/")
async def get_appointments(current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    cursor = db.appointments.find({"patient_id": current_user["_id"]}, sort=[("scheduled_at", -1)], limit=20)
    appts = await cursor.to_list(length=20)
    return [{"id": a["_id"], "appointment_type": a["appointment_type"], "status": a["status"], "scheduled_at": a["scheduled_at"], "is_telemedicine": a.get("is_telemedicine", False)} for a in appts]


@router.post("/", status_code=201)
async def create_appointment(request: CreateAppointmentRequest, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    appt_id = str(uuid.uuid4())
    doc = {
        "_id": appt_id,
        "patient_id": current_user["_id"],
        "appointment_type": request.appointment_type,
        "scheduled_at": request.scheduled_at,
        "duration_minutes": request.duration_minutes,
        "is_telemedicine": request.is_telemedicine,
        "reason": request.reason,
        "priority": request.priority,
        "status": "scheduled",
        "created_at": now,
    }
    await db.appointments.insert_one(doc)
    return {"id": appt_id, "status": "scheduled", "scheduled_at": request.scheduled_at}


@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: str, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    result = await db.appointments.update_one(
        {"_id": appointment_id, "patient_id": current_user["_id"]},
        {"$set": {"status": "cancelled"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"success": True}
