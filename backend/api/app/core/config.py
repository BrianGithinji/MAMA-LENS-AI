"""MAMA-LENS AI — Application Configuration"""
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "MAMA-LENS AI"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "dev-secret-key-mamalens-2026-change-in-prod"
    DEBUG: bool = True

    # MongoDB — SRV format works on all platforms including Render
    MONGODB_URI: str = (
        "mongodb+srv://BrianGithinji:BrianMAMA@"
        "mama.e5o71yv.mongodb.net/"
        "?retryWrites=true&w=majority&appName=MAMA"
    )
    MONGODB_DB_NAME: str = "mamalens"

    # JWT
    JWT_SECRET_KEY: str = "dev-jwt-secret-mamalens-2026-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = "1955475168-giiefrpni7di4s9i9b7v6mgtmpa22emp.apps.googleusercontent.com"

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""

    # LiveKit
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_URL: str = "wss://localhost:7880"

    # WhatsApp
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = "mamalens-webhook-token"

    # Africa's Talking
    AFRICASTALKING_API_KEY: str = ""
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_SENDER_ID: str = "MAMALENS"

    # CORS — use ["*"] in production to allow any Netlify/custom domain
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            import json
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
