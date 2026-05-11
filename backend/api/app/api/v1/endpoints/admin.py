from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


async def require_admin(current_user: dict = Depends(get_current_active_user)) -> dict:
    if current_user.get("role") != "system_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/dashboard")
async def admin_dashboard(admin: dict = Depends(require_admin)):
    db = get_db()
    total_users = await db.users.count_documents({})
    total_assessments = await db.risk_assessments.count_documents({})
    emergency_count = await db.risk_assessments.count_documents({"is_emergency": True})
    return {
        "total_users": total_users,
        "total_risk_assessments": total_assessments,
        "emergency_alerts_total": emergency_count,
        "platform": "MAMA-LENS AI",
        "version": "1.0.0",
    }
