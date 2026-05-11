import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
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


# ─── Community (Mental Health) ────────────────────────────────────────────────

class CommunityPostRequest(BaseModel):
    content: str
    topic: str = "general"  # general | anxiety | grief | postpartum | nutrition
    is_anonymous: bool = False


class CommunityReplyRequest(BaseModel):
    content: str
    is_anonymous: bool = False


def _display_name(user: dict, anonymous: bool) -> str:
    if anonymous:
        return "Anonymous Mama"
    first = user.get("first_name", "")
    last = user.get("last_name", "")
    return f"{first} {last[0]}." if last else first or "Mama"


@router.get("/community")
async def get_community_posts(
    topic: Optional[str] = None,
    limit: int = 30,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    query = {"topic": topic} if topic and topic != "all" else {}
    cursor = db.community_posts.find(query, sort=[("created_at", -1)], limit=limit)
    posts = await cursor.to_list(length=limit)
    return [
        {
            "id": p["_id"],
            "content": p["content"],
            "topic": p["topic"],
            "author": p["author_display"],
            "is_own": p["user_id"] == current_user["_id"],
            "reply_count": len(p.get("replies", [])),
            "replies": [
                {
                    "id": r["_id"],
                    "content": r["content"],
                    "author": r["author_display"],
                    "is_own": r["user_id"] == current_user["_id"],
                    "created_at": r["created_at"],
                }
                for r in p.get("replies", [])
            ],
            "created_at": p["created_at"],
        }
        for p in posts
    ]


@router.post("/community", status_code=201)
async def create_community_post(
    request: CommunityPostRequest,
    current_user: dict = Depends(get_current_active_user),
):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Post content cannot be empty")
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    post_id = str(uuid.uuid4())
    doc = {
        "_id": post_id,
        "user_id": current_user["_id"],
        "author_display": _display_name(current_user, request.is_anonymous),
        "content": request.content.strip(),
        "topic": request.topic,
        "replies": [],
        "created_at": now,
    }
    await db.community_posts.insert_one(doc)
    return {"id": post_id, "author": doc["author_display"], "created_at": now}


@router.post("/community/{post_id}/reply", status_code=201)
async def reply_to_post(
    post_id: str,
    request: CommunityReplyRequest,
    current_user: dict = Depends(get_current_active_user),
):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Reply cannot be empty")
    db = get_db()
    post = await db.community_posts.find_one({"_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    now = datetime.now(timezone.utc).isoformat()
    reply = {
        "_id": str(uuid.uuid4()),
        "user_id": current_user["_id"],
        "author_display": _display_name(current_user, request.is_anonymous),
        "content": request.content.strip(),
        "created_at": now,
    }
    await db.community_posts.update_one(
        {"_id": post_id},
        {"$push": {"replies": reply}},
    )
    return {"id": reply["_id"], "author": reply["author_display"], "created_at": now}


@router.delete("/community/{post_id}")
async def delete_community_post(
    post_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    result = await db.community_posts.delete_one(
        {"_id": post_id, "user_id": current_user["_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found or not yours")
    return {"success": True}
