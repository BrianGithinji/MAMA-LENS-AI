"""
MAMA-LENS AI — API v1 Router
Aggregates all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    pregnancy,
    risk_assessment,
    health_records,
    appointments,
    telemedicine,
    messages,
    facilities,
    wearables,
    notifications,
    ai_avatar,
    education,
    whatsapp,
    sms_ussd,
    admin,
)

api_router = APIRouter()

# ─── Authentication ───────────────────────────────────────────────────────────
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# ─── Users ───────────────────────────────────────────────────────────────────
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# ─── Pregnancy ───────────────────────────────────────────────────────────────
api_router.include_router(pregnancy.router, prefix="/pregnancy", tags=["Pregnancy"])

# ─── Risk Assessment ─────────────────────────────────────────────────────────
api_router.include_router(risk_assessment.router, prefix="/risk", tags=["Risk Assessment"])

# ─── Health Records ──────────────────────────────────────────────────────────
api_router.include_router(health_records.router, prefix="/health-records", tags=["Health Records"])

# ─── Appointments ────────────────────────────────────────────────────────────
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])

# ─── Telemedicine ────────────────────────────────────────────────────────────
api_router.include_router(telemedicine.router, prefix="/telemedicine", tags=["Telemedicine"])

# ─── Messaging ───────────────────────────────────────────────────────────────
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])

# ─── Healthcare Facilities ───────────────────────────────────────────────────
api_router.include_router(facilities.router, prefix="/facilities", tags=["Facilities"])

# ─── Wearables & IoT ─────────────────────────────────────────────────────────
api_router.include_router(wearables.router, prefix="/wearables", tags=["Wearables & IoT"])

# ─── Notifications ───────────────────────────────────────────────────────────
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# ─── AI Avatar ───────────────────────────────────────────────────────────────
api_router.include_router(ai_avatar.router, prefix="/avatar", tags=["AI Avatar"])

# ─── Education ───────────────────────────────────────────────────────────────
api_router.include_router(education.router, prefix="/education", tags=["Education"])

# ─── WhatsApp Bot ────────────────────────────────────────────────────────────
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])

# ─── SMS / USSD ──────────────────────────────────────────────────────────────
api_router.include_router(sms_ussd.router, prefix="/sms-ussd", tags=["SMS & USSD"])

# ─── Admin ───────────────────────────────────────────────────────────────────
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
