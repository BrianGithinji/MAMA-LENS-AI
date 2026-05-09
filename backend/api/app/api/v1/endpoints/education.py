"""MAMA-LENS AI — Education Endpoints (MongoDB)"""
import sys
import os
from fastapi import APIRouter, Depends, Query
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()

_NLP_PATH = os.path.join(os.path.dirname(__file__), "../../../../../../ai/nlp")
_REC_PATH = os.path.join(os.path.dirname(__file__), "../../../../../../ai/recommendation")
for p in [_NLP_PATH, _REC_PATH]:
    if p not in sys.path:
        sys.path.insert(0, p)


@router.get("/weekly/{week}")
async def get_weekly_education(
    week: int,
    language: str = Query(default="en"),
    current_user: dict = Depends(get_current_active_user),
):
    try:
        from conversation_ai import ConversationalAI
        ai = ConversationalAI()
        content = ai.get_weekly_education(week, language)
        return {"week": week, "language": language, "content": content}
    except Exception:
        return {"week": week, "language": language, "content": f"Week {week}: Continue attending your ANC visits and taking your supplements."}


@router.get("/recommendations")
async def get_recommendations(
    gestational_age_weeks: int = Query(...),
    risk_level: str = Query(default="low"),
    language: str = Query(default="en"),
    current_user: dict = Depends(get_current_active_user),
):
    try:
        from recommendation_engine import RecommendationEngine, UserProfile
        engine = RecommendationEngine()
        profile = UserProfile(
            user_id=current_user["_id"],
            age=28,
            gestational_age_weeks=gestational_age_weeks,
            language=language,
            risk_level=risk_level,
        )
        plan = engine.generate_plan(profile)
        return {
            "gestational_age_weeks": gestational_age_weeks,
            "risk_level": risk_level,
            "next_anc_date": plan.next_anc_date,
            "weekly_education": plan.weekly_education,
            "top_recommendations": [
                {"title": r.title, "urgency": r.urgency.value, "category": r.category.value, "description": r.description}
                for r in plan.recommendations[:5]
            ],
        }
    except Exception as e:
        return {"error": str(e), "message": "Recommendations temporarily unavailable"}


@router.get("/danger-signs")
async def get_danger_signs(language: str = Query(default="en")):
    data = {
        "en": {
            "title": "Pregnancy Danger Signs",
            "subtitle": "Go to hospital IMMEDIATELY if you experience:",
            "signs": [
                "Heavy vaginal bleeding", "Severe headache with vision changes",
                "Severe abdominal pain", "Baby not moving (after 28 weeks)",
                "Seizures or fits", "High fever", "Difficulty breathing",
                "Severe swelling of face and hands",
            ],
            "emergency_numbers": ["999", "112"],
        },
        "sw": {
            "title": "Dalili za Hatari za Ujauzito",
            "subtitle": "Nenda hospitali MARA MOJA ukiwa na:",
            "signs": [
                "Kutoka damu nyingi ukeni", "Maumivu makali ya kichwa na mabadiliko ya maono",
                "Maumivu makali ya tumbo", "Mtoto hasogei (baada ya wiki 28)",
                "Degedege", "Homa kali", "Ugumu wa kupumua",
                "Uvimbe mkubwa wa uso na mikono",
            ],
            "emergency_numbers": ["999", "112"],
        },
    }
    return data.get(language, data["en"])
