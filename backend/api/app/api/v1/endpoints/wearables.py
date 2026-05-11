import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/devices")
async def get_devices(current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    cursor = db.wearable_devices.find({"user_id": current_user["_id"]})
    devices = await cursor.to_list(length=20)
    return [{"id": d["_id"], "device_type": d["device_type"], "device_name": d["device_name"], "is_active": d.get("is_active", True)} for d in devices]


@router.post("/readings", status_code=201)
async def submit_reading(reading: dict, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    reading_id = str(uuid.uuid4())
    doc = {
        "_id": reading_id,
        "device_id": reading.get("device_id", "manual"),
        "user_id": current_user["_id"],
        "reading_type": reading.get("reading_type", "vitals"),
        "value": reading.get("value"),
        "value_secondary": reading.get("value_secondary"),
        "unit": reading.get("unit"),
        "recorded_at": reading.get("recorded_at", now),
        "context": reading.get("context"),
        "is_abnormal": False,
        "alert_triggered": False,
        "created_at": now,
    }
    await db.wearable_readings.insert_one(doc)
    return {"id": reading_id, "alert_triggered": False}
