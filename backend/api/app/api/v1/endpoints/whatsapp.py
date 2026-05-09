"""MAMA-LENS AI — WhatsApp Webhook Endpoints (MongoDB)"""
import sys
import os
from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from app.core.config import settings

router = APIRouter()

_NLP_PATH = os.path.join(os.path.dirname(__file__), "../../../../../../ai/nlp")
if _NLP_PATH not in sys.path:
    sys.path.insert(0, _NLP_PATH)


@router.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        return int(params.get("hub.challenge", 0))
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    background_tasks.add_task(_process_webhook, payload)
    return {"status": "ok"}


async def _process_webhook(payload: dict):
    try:
        entry = payload.get("entry", [{}])[0]
        messages = entry.get("changes", [{}])[0].get("value", {}).get("messages", [])
        for message in messages:
            from_number = message.get("from", "")
            content = message.get("text", {}).get("body", "")
            if not content:
                continue
            try:
                from conversation_ai import ConversationalAI
                ai = ConversationalAI(openai_api_key=settings.OPENAI_API_KEY)
                response = ai.chat(session_id=f"wa_{from_number}", user_message=content, channel="whatsapp")
                print(f"WhatsApp → {from_number[:6]}****: {response.message[:80]}")
            except Exception as e:
                print(f"WhatsApp AI error: {e}")
    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
