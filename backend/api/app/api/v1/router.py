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

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(pregnancy.router, prefix="/pregnancy", tags=["Pregnancy"])
api_router.include_router(risk_assessment.router, prefix="/risk", tags=["Risk Assessment"])
api_router.include_router(health_records.router, prefix="/health-records", tags=["Health Records"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(telemedicine.router, prefix="/telemedicine", tags=["Telemedicine"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(facilities.router, prefix="/facilities", tags=["Facilities"])
api_router.include_router(wearables.router, prefix="/wearables", tags=["Wearables & IoT"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(ai_avatar.router, prefix="/avatar", tags=["AI Avatar"])
api_router.include_router(education.router, prefix="/education", tags=["Education"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
api_router.include_router(sms_ussd.router, prefix="/sms-ussd", tags=["SMS & USSD"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
