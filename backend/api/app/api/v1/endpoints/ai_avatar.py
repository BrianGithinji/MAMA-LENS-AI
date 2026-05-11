import io
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
import structlog

from app.core.config import settings
from app.api.v1.endpoints.auth import get_current_active_user

logger = structlog.get_logger(__name__)
router = APIRouter()

try:
    from app.conversation_ai import ConversationalAI
    from app.emotion_detector import EmotionDetector, EmotionInput
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False


class AvatarChatRequest:
    def __init__(self, message: str, language: str = "en", session_id: str = "",
                 gestational_age_weeks: Optional[int] = None, context: Optional[str] = None,
                 voice_response: bool = False):
        self.message = message
        self.language = language
        self.session_id = session_id
        self.gestational_age_weeks = gestational_age_weeks
        self.context = context
        self.voice_response = voice_response


from pydantic import BaseModel

class AvatarChatRequestModel(BaseModel):
    message: str
    language: str = "en"
    session_id: str = ""
    gestational_age_weeks: Optional[int] = None
    context: Optional[str] = None
    voice_response: bool = False


@router.post("/chat")
async def avatar_chat(
    request: AvatarChatRequestModel,
    current_user: dict = Depends(get_current_active_user),
):
    text_response = ""
    intent = "general_question"
    is_emergency = False
    suggested_actions = []
    emotion_detected = None

    if not _AI_AVAILABLE:
        text_response = "I'm here to support you. How are you feeling today?"
    else:
        try:
            ai = ConversationalAI(openai_api_key=settings.OPENAI_API_KEY)
            response = ai.chat(
                session_id=request.session_id or current_user["_id"],
                user_message=request.message,
                language=request.language,
                channel="app",
                gestational_age_weeks=request.gestational_age_weeks,
            )
            text_response = response.message
            intent = response.intent.value
            is_emergency = response.is_emergency
            suggested_actions = response.suggested_actions
        except Exception as e:
            logger.warning("AI chat fallback", error=str(e))
            text_response = "I'm here to support you. How are you feeling today?"

        try:
            detector = EmotionDetector()
            emotion_result = detector.detect(EmotionInput(
                text=request.message,
                context=request.context or "",
                language=request.language,
            ))
            emotion_detected = emotion_result.primary_emotion.value
            if emotion_result.crisis_detected:
                text_response = emotion_result.compassionate_response
                is_emergency = True
        except Exception as e:
            logger.warning("Emotion detection fallback", error=str(e))

    return {
        "text_response": text_response,
        "audio_url": None,
        "emotion_detected": emotion_detected,
        "intent": intent,
        "is_emergency": is_emergency,
        "suggested_actions": suggested_actions,
    }


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="auto"),
    current_user: dict = Depends(get_current_active_user),
):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
    try:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        audio_data = await audio.read()
        audio_file = io.BytesIO(audio_data)
        audio_file.name = audio.filename or "audio.webm"
        kwargs = {"model": "whisper-1", "file": audio_file}
        if language != "auto":
            kwargs["language"] = language
        transcript = client.audio.transcriptions.create(**kwargs)
        return {"text": transcript.text, "language": language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/realtime-token")
async def get_realtime_token(current_user: dict = Depends(get_current_active_user)):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
    try:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.beta.realtime.sessions.create(
            model=settings.OPENAI_MODEL,
            voice="alloy",
            instructions=(
                "You are MAMA, a compassionate AI maternal health assistant for MAMA-LENS AI. "
                "You support pregnant women and new mothers in Africa with warmth and cultural sensitivity."
            ),
        )
        return {"client_secret": response.client_secret.value, "model": settings.OPENAI_MODEL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
