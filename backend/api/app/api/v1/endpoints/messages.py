"""MAMA-LENS AI — Messaging Endpoints (MongoDB)"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_messages(limit: int = 50, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    cursor = db.messages.find({"user_id": current_user["_id"]}, sort=[("created_at", -1)], limit=limit)
    msgs = await cursor.to_list(length=limit)
    return [{"id": m["_id"], "content": m.get("content"), "direction": m["direction"], "channel": m["channel"], "created_at": m["created_at"]} for m in msgs]


@router.post("/chat")
async def send_chat_message(message: dict, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    msg_id = str(uuid.uuid4())
    doc = {
        "_id": msg_id,
        "user_id": current_user["_id"],
        "channel": message.get("channel", "app"),
        "message_type": "text",
        "direction": "inbound",
        "content": message.get("content", ""),
        "language": message.get("language", "en"),
        "created_at": now,
    }
    await db.messages.insert_one(doc)
    return {"id": msg_id, "status": "sent"}
