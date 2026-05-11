import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

logger = structlog.get_logger(__name__)
router = APIRouter()

try:
    from app.risk_engine import MaternalRiskEngine, RiskInput, NutritionStatus
    _RISK_ENGINE_AVAILABLE = True
except ImportError:
    _RISK_ENGINE_AVAILABLE = False


class RiskAssessmentRequest(BaseModel):
    age: int = Field(..., ge=10, le=60)
    gestational_age_weeks: int = Field(..., ge=1, le=42)
    systolic_bp: float = Field(..., ge=60, le=250)
    diastolic_bp: float = Field(..., ge=40, le=150)
    blood_glucose: float = Field(..., ge=40, le=500)
    heart_rate: float = Field(..., ge=40, le=200)
    hemoglobin: float = Field(..., ge=3, le=20)
    weight_kg: float = Field(..., ge=30, le=200)
    height_cm: float = Field(..., ge=100, le=220)
    previous_miscarriages: int = Field(default=0, ge=0)
    previous_preeclampsia: bool = False
    previous_gestational_diabetes: bool = False
    previous_preterm_birth: bool = False
    is_multiple_pregnancy: bool = False
    smoking: bool = False
    alcohol_use: bool = False
    stress_level: int = Field(default=5, ge=1, le=10)
    nutrition_status: str = "fair"
    pre_existing_conditions: List[str] = []
    reported_symptoms: List[str] = []
    pregnancy_profile_id: Optional[str] = None
    assessment_type: str = "routine"
    language: str = "en"


@router.post("/assess", status_code=status.HTTP_201_CREATED)
async def assess_risk(
    request: RiskAssessmentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user),
):
    if not _RISK_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Risk engine unavailable: module not found")

    nutrition_map = {
        "poor": NutritionStatus.POOR, "fair": NutritionStatus.FAIR,
        "good": NutritionStatus.GOOD, "excellent": NutritionStatus.EXCELLENT,
    }

    risk_input = RiskInput(
        age=request.age,
        gestational_age_weeks=request.gestational_age_weeks,
        systolic_bp=request.systolic_bp,
        diastolic_bp=request.diastolic_bp,
        blood_glucose=request.blood_glucose,
        heart_rate=request.heart_rate,
        hemoglobin=request.hemoglobin,
        weight_kg=request.weight_kg,
        height_cm=request.height_cm,
        previous_miscarriages=request.previous_miscarriages,
        previous_preeclampsia=request.previous_preeclampsia,
        previous_gestational_diabetes=request.previous_gestational_diabetes,
        previous_preterm_birth=request.previous_preterm_birth,
        is_multiple_pregnancy=request.is_multiple_pregnancy,
        smoking=request.smoking,
        alcohol_use=request.alcohol_use,
        stress_level=request.stress_level,
        nutrition_status=nutrition_map.get(request.nutrition_status, NutritionStatus.FAIR),
        pre_existing_conditions=request.pre_existing_conditions,
        reported_symptoms=request.reported_symptoms,
        language=request.language,
    )

    engine = MaternalRiskEngine(language=request.language)
    result = engine.assess_risk(risk_input)

    now = datetime.now(timezone.utc).isoformat()
    assessment_id = str(uuid.uuid4())

    doc = {
        "_id": assessment_id,
        "user_id": current_user["_id"],
        "pregnancy_profile_id": request.pregnancy_profile_id,
        "overall_risk_level": result.overall_risk_level.value,
        "overall_risk_score": result.overall_risk_score,
        "confidence_score": result.confidence_score,
        "miscarriage_risk_score": result.miscarriage_risk_score,
        "preeclampsia_risk_score": result.preeclampsia_risk_score,
        "gestational_diabetes_risk_score": result.gestational_diabetes_risk_score,
        "anemia_risk_score": result.anemia_risk_score,
        "preterm_birth_risk_score": result.preterm_birth_risk_score,
        "input_data": request.dict(),
        "risk_factors": result.risk_factors,
        "protective_factors": result.protective_factors,
        "recommendations": result.recommendations,
        "immediate_actions": result.immediate_actions,
        "is_emergency": result.is_emergency,
        "emergency_type": result.emergency_type,
        "model_version": result.model_version,
        "assessment_type": request.assessment_type,
        "created_at": now,
    }

    db = get_db()
    await db.risk_assessments.insert_one(doc)

    if result.is_emergency:
        background_tasks.add_task(_log_emergency, current_user["_id"], result.emergency_type)

    risk_labels = {
        "low": "Low Risk", "moderate": "Moderate Risk",
        "high": "High Risk", "emergency": "Emergency",
    }

    logger.info("Risk assessment", user_id=current_user["_id"], level=result.overall_risk_level.value)

    return {
        "assessment_id": assessment_id,
        "overall_risk_level": result.overall_risk_level.value,
        "overall_risk_score": result.overall_risk_score,
        "confidence_score": result.confidence_score,
        "risk_level_display": risk_labels.get(result.overall_risk_level.value, "Unknown"),
        "miscarriage_risk_score": result.miscarriage_risk_score,
        "preeclampsia_risk_score": result.preeclampsia_risk_score,
        "gestational_diabetes_risk_score": result.gestational_diabetes_risk_score,
        "anemia_risk_score": result.anemia_risk_score,
        "preterm_birth_risk_score": result.preterm_birth_risk_score,
        "risk_factors": result.risk_factors,
        "protective_factors": result.protective_factors,
        "recommendations": result.recommendations,
        "immediate_actions": result.immediate_actions,
        "is_emergency": result.is_emergency,
        "emergency_type": result.emergency_type,
        "next_assessment_days": result.next_assessment_days,
        "model_version": result.model_version,
        "bias_notes": result.bias_notes,
    }


@router.get("/history")
async def get_risk_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    cursor = db.risk_assessments.find(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
        limit=limit,
    )
    assessments = await cursor.to_list(length=limit)
    return [
        {
            "id": a["_id"],
            "overall_risk_level": a["overall_risk_level"],
            "overall_risk_score": a["overall_risk_score"],
            "is_emergency": a["is_emergency"],
            "assessment_type": a.get("assessment_type", "routine"),
            "created_at": a["created_at"],
        }
        for a in assessments
    ]


@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    a = await db.risk_assessments.find_one(
        {"_id": assessment_id, "user_id": current_user["_id"]}
    )
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    risk_labels = {
        "low": "Low Risk", "moderate": "Moderate Risk",
        "high": "High Risk", "emergency": "Emergency",
    }
    return {
        "assessment_id": a["_id"],
        "overall_risk_level": a["overall_risk_level"],
        "overall_risk_score": a["overall_risk_score"],
        "confidence_score": a["confidence_score"],
        "risk_level_display": risk_labels.get(a["overall_risk_level"], "Unknown"),
        "miscarriage_risk_score": a.get("miscarriage_risk_score", 0),
        "preeclampsia_risk_score": a.get("preeclampsia_risk_score", 0),
        "gestational_diabetes_risk_score": a.get("gestational_diabetes_risk_score", 0),
        "anemia_risk_score": a.get("anemia_risk_score", 0),
        "preterm_birth_risk_score": a.get("preterm_birth_risk_score", 0),
        "risk_factors": a.get("risk_factors", []),
        "protective_factors": a.get("protective_factors", []),
        "recommendations": a.get("recommendations", []),
        "immediate_actions": a.get("immediate_actions", []),
        "is_emergency": a["is_emergency"],
        "emergency_type": a.get("emergency_type"),
        "next_assessment_days": 7,
        "model_version": a.get("model_version", "1.0.0"),
        "bias_notes": [],
    }


@router.post("/symptom-check")
async def quick_symptom_check(
    symptoms: List[str],
    gestational_age_weeks: int,
    language: str = "en",
    current_user: dict = Depends(get_current_active_user),
):
    DANGER_SIGNS = {
        "heavy_bleeding": {"en": "Heavy bleeding is a danger sign. Go to hospital immediately.", "sw": "Damu nyingi ni dalili ya hatari. Nenda hospitali mara moja."},
        "severe_headache": {"en": "Severe headache may indicate preeclampsia. Seek care now.", "sw": "Maumivu makali ya kichwa yanaweza kuonyesha preeclampsia."},
        "no_fetal_movement": {"en": "Reduced fetal movement requires immediate evaluation.", "sw": "Kupungua kwa mwendo wa mtoto kunahitaji tathmini ya haraka."},
        "seizure": {"en": "Seizure is a medical emergency. Call 999 immediately.", "sw": "Degedege ni dharura ya kimatibabu."},
        "vision_changes": {"en": "Sudden vision changes may indicate preeclampsia.", "sw": "Mabadiliko ya ghafla ya maono yanaweza kuonyesha preeclampsia."},
        "difficulty_breathing": {"en": "Difficulty breathing requires immediate attention.", "sw": "Ugumu wa kupumua unahitaji msaada wa haraka."},
    }
    flags = []
    is_emergency = False
    for symptom in symptoms:
        key = symptom.lower().replace(" ", "_")
        if key in DANGER_SIGNS:
            msg = DANGER_SIGNS[key].get(language, DANGER_SIGNS[key]["en"])
            flags.append({"symptom": symptom, "message": msg, "is_danger_sign": True})
            is_emergency = True

    if not flags:
        return {"is_emergency": False, "flags": [], "message": "No immediate danger signs detected."}
    return {"is_emergency": is_emergency, "flags": flags, "message": "⚠️ Danger signs detected. Please seek medical care immediately."}


async def _log_emergency(user_id: str, emergency_type: str):
    logger.warning("EMERGENCY ALERT", user_id=user_id, emergency_type=emergency_type)
