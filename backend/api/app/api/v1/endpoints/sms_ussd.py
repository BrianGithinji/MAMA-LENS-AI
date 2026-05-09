"""MAMA-LENS AI — SMS & USSD Endpoints (MongoDB)"""
from fastapi import APIRouter, Form, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from app.core.config import settings

router = APIRouter()

try:
    from app.conversation_ai import ConversationalAI
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

USSD_MAIN = {
    "en": "CON Welcome to MAMA-LENS AI\nMaternal Health Support\n\n1. Check symptoms\n2. Pregnancy info\n3. Find clinic\n4. Emergency help\n5. Mental health support",
    "sw": "CON Karibu MAMA-LENS AI\nMsaada wa Afya ya Uzazi\n\n1. Angalia dalili\n2. Habari za ujauzito\n3. Tafuta kliniki\n4. Msaada wa dharura\n5. Msaada wa afya ya akili",
}

USSD_EMERGENCY = {
    "en": "END EMERGENCY\n\nCall: 999 or 112\n\nDanger signs:\n- Heavy bleeding\n- Severe headache\n- Baby not moving\n- Seizures\n\nGo to hospital NOW",
    "sw": "END DHARURA\n\nPiga: 999 au 112\n\nDalili za hatari:\n- Damu nyingi\n- Maumivu makali ya kichwa\n- Mtoto hasogei\n- Degedege\n\nNenda hospitali SASA",
}


@router.post("/ussd", response_class=PlainTextResponse)
async def handle_ussd(
    sessionId: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(default=""),
):
    lang = "en"
    steps = [s for s in text.split("*") if s] if text else []
    level1 = steps[0] if steps else ""

    if level1 == "4":
        return USSD_EMERGENCY.get(lang, USSD_EMERGENCY["en"])
    elif level1 == "3":
        return "END Find clinic: Visit mamalens.ai/clinics\nOr call: 0800 720 999\nEmergency: 999 / 112"
    elif level1 == "5":
        return "END Mental Health Support\n\nYou are not alone.\nCall: +254 722 178 177\nText MAMA to 40404"
    else:
        return USSD_MAIN.get(lang, USSD_MAIN["en"])


@router.post("/sms/incoming")
async def handle_sms(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    from_number = form.get("from", "")
    message = form.get("text", "").lower().strip()

    responses = {
        "help": "MAMA-LENS: Reply SYMPTOMS, CLINIC, EMERGENCY, NUTRITION, SUPPORT. Emergency: 999",
        "emergency": "EMERGENCY: Call 999/112 NOW. Heavy bleeding, severe headache, baby not moving = go to hospital immediately.",
        "clinic": "Find clinic: mamalens.ai/clinics or call 0800 720 999. Emergency: 999/112",
        "nutrition": "Eat: beans, dark greens, eggs, fish. Drink 8+ glasses water. Take iron+folic acid. Avoid alcohol.",
        "support": "You are not alone. Call +254 722 178 177 for mental health support.",
    }
    reply = responses.get(message, "MAMA-LENS: Reply HELP for options. Emergency: 999")
    return {"status": "received", "reply": reply}
