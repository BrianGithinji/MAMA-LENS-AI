"""MAMA-LENS AI — Notification Endpoints (MongoDB)"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_notifications(
    limit: int = 20,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    query: dict = {"user_id": current_user["_id"]}
    if unread_only:
        query["is_read"] = False
    cursor = db.notifications.find(query, sort=[("created_at", -1)], limit=limit)
    notifications = await cursor.to_list(length=limit)
    return [
        {
            "id": n["_id"],
            "title": n["title"],
            "body": n["body"],
            "is_read": n.get("is_read", False),
            "notification_type": n.get("notification_type", "system_message"),
            "created_at": n["created_at"],
        }
        for n in notifications
    ]


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    await db.notifications.update_one(
        {"_id": notification_id, "user_id": current_user["_id"]},
        {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True}
