"""MAMA-LENS AI — User Profile Endpoints (MongoDB)"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_active_user)):
    return {
        "id": current_user["_id"],
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "email": current_user.get("email"),
        "phone_number": current_user.get("phone_number"),
        "role": current_user["role"],
        "preferred_language": current_user.get("preferred_language", "en"),
        "country": current_user.get("country"),
        "status": current_user.get("status", "active"),
        "onboarding_completed": current_user.get("onboarding_completed", False),
        "data_consent_given": current_user.get("data_consent_given", False),
    }


@router.put("/me")
async def update_my_profile(
    updates: dict,
    current_user: dict = Depends(get_current_active_user),
):
    allowed = ["first_name", "last_name", "preferred_language", "country",
               "region", "fcm_token", "onboarding_completed"]
    safe = {k: v for k, v in updates.items() if k in allowed}
    safe["updated_at"] = datetime.now(timezone.utc).isoformat()

    db = get_db()
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": safe})
    return {"success": True, "message": "Profile updated"}
