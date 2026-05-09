"""
MAMA-LENS AI - Maternal Risk Assessment Engine
Core AI engine for assessing maternal health risks during pregnancy.
Supports rule-based scoring with ML model fallback.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EMERGENCY = "emergency"


class NutritionStatus(str, Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


# ---------------------------------------------------------------------------
# Input / Output models
# ---------------------------------------------------------------------------

@dataclass
class RiskInput:
    """All clinical and lifestyle inputs required for risk assessment."""

    # Demographics
    age: int
    gestational_age_weeks: int

    # Vitals
    systolic_bp: float
    diastolic_bp: float
    blood_glucose: float          # mg/dL fasting
    heart_rate: float
    hemoglobin: float             # g/dL
    weight_kg: float
    height_cm: float

    # Obstetric history
    previous_miscarriages: int = 0
    previous_preeclampsia: bool = False
    previous_gestational_diabetes: bool = False
    previous_preterm_birth: bool = False
    is_multiple_pregnancy: bool = False

    # Lifestyle
    smoking: bool = False
    alcohol_use: bool = False
    stress_level: int = 5         # 1-10
    nutrition_status: NutritionStatus = NutritionStatus.FAIR

    # Medical
    pre_existing_conditions: List[str] = field(default_factory=list)
    reported_symptoms: List[str] = field(default_factory=list)

    # Metadata
    language: str = "en"
    literacy_level: str = "medium"  # low / medium / high

    @property
    def bmi(self) -> float:
        if self.height_cm <= 0:
            return 0.0
        return self.weight_kg / ((self.height_cm / 100) ** 2)


@dataclass
class RiskFactor:
    factor: str
    weight: float          # 0-1 contribution to overall score
    description: str
    is_modifiable: bool = True


@dataclass
class RiskOutput:
    """Complete risk assessment output with explanations and recommendations."""

    # Overall
    overall_risk_level: RiskLevel
    overall_risk_score: float      # 0-1
    confidence_score: float        # 0-1

    # Condition-specific scores
    miscarriage_risk_score: float
    preeclampsia_risk_score: float
    gestational_diabetes_risk_score: float
    anemia_risk_score: float
    preterm_birth_risk_score: float

    # Explanations
    risk_factors: List[Dict[str, Any]]
    protective_factors: List[str]

    # Actions
    recommendations: List[str]
    immediate_actions: List[str]

    # Emergency
    is_emergency: bool
    emergency_type: Optional[str]

    # Follow-up
    next_assessment_days: int

    # Metadata
    assessment_timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    model_version: str = "1.0.0"
    bias_notes: List[str] = field(default_factory=list)



# ---------------------------------------------------------------------------
# Multilingual recommendations
# ---------------------------------------------------------------------------

RECOMMENDATIONS_I18N: Dict[str, Dict[str, str]] = {
    "attend_anc": {
        "en": "Attend all scheduled antenatal care (ANC) visits.",
        "sw": "Hudhuria kliniki zote za uzazi ulizopangwa.",
        "fr": "Assistez a toutes les visites de soins prenatals programmees.",
        "ar": "احضري جميع زيارات الرعاية السابقة للولادة المجدولة.",
    },
    "monitor_bp": {
        "en": "Monitor your blood pressure daily and record readings.",
        "sw": "Pima shinikizo la damu kila siku na kuandika matokeo.",
        "fr": "Surveillez votre tension arterielle quotidiennement.",
        "ar": "راقبي ضغط دمك يوميا وسجلي القراءات.",
    },
    "iron_supplement": {
        "en": "Take iron and folic acid supplements as prescribed.",
        "sw": "Chukua virutubisho vya chuma na asidi ya foliki kama ilivyoagizwa.",
        "fr": "Prenez des supplements de fer et d acide folique comme prescrit.",
        "ar": "تناولي مكملات الحديد وحمض الفوليك كما وصف الطبيب.",
    },
    "hydration": {
        "en": "Drink at least 8-10 glasses of clean water daily.",
        "sw": "Kunywa angalau glasi 8-10 za maji safi kila siku.",
        "fr": "Buvez au moins 8 a 10 verres d eau propre par jour.",
        "ar": "اشربي ما لا يقل عن 8-10 اكواب من الماء النظيف يوميا.",
    },
    "rest": {
        "en": "Rest adequately and avoid heavy physical exertion.",
        "sw": "Pumzika vizuri na epuka kazi nzito za kimwili.",
        "fr": "Reposez-vous suffisamment et evitez les efforts physiques intenses.",
        "ar": "استريحي بشكل كاف وتجنبي المجهود البدني الشاق.",
    },
    "nutrition": {
        "en": "Eat a balanced diet rich in iron, protein, and vitamins.",
        "sw": "Kula chakula chenye lishe bora chenye chuma, protini, na vitamini.",
        "fr": "Mangez un regime equilibre riche en fer, proteines et vitamines.",
        "ar": "تناولي نظاما غذائيا متوازنا غنيا بالحديد والبروتين والفيتامينات.",
    },
    "emergency_visit": {
        "en": "Go to the nearest health facility IMMEDIATELY.",
        "sw": "Nenda kituo cha afya kilicho karibu MARA MOJA.",
        "fr": "Rendez-vous IMMEDIATEMENT a l etablissement de sante le plus proche.",
        "ar": "اذهبي فورا الى اقرب مرفق صحي.",
    },
    "glucose_monitoring": {
        "en": "Monitor blood glucose levels as directed by your healthcare provider.",
        "sw": "Pima viwango vya sukari ya damu kama ilivyoelekezwa na mtoa huduma wako.",
        "fr": "Surveillez votre glycemie comme indique par votre prestataire de soins.",
        "ar": "راقبي مستويات الجلوكوز في الدم كما وجهك مقدم الرعاية الصحية.",
    },
    "stop_smoking": {
        "en": "Stop smoking immediately - it harms your baby.",
        "sw": "Acha kuvuta sigara mara moja - inadhuru mtoto wako.",
        "fr": "Arretez de fumer immediatement - cela nuit a votre bebe.",
        "ar": "توقفي عن التدخين فورا - فهو يضر بطفلك.",
    },
    "mental_health": {
        "en": "Seek emotional support from family, friends, or a counselor.",
        "sw": "Tafuta msaada wa kihisia kutoka kwa familia, marafiki, au mshauri.",
        "fr": "Cherchez un soutien emotionnel aupres de la famille, des amis ou d un conseiller.",
        "ar": "اطلبي الدعم العاطفي من العائلة والاصدقاء او المستشار.",
    },
}

EMERGENCY_SYMPTOMS = {
    "severe_headache", "vision_changes", "blurred_vision", "severe_abdominal_pain",
    "chest_pain", "difficulty_breathing", "heavy_bleeding", "no_fetal_movement",
    "seizure", "loss_of_consciousness", "severe_swelling", "high_fever",
    "foul_smelling_discharge", "cord_prolapse",
}

PREECLAMPSIA_SYMPTOMS = {
    "headache", "vision_changes", "upper_abdominal_pain", "nausea",
    "vomiting", "swelling_face", "swelling_hands", "sudden_weight_gain",
}


# ---------------------------------------------------------------------------
# MaternalRiskEngine
# ---------------------------------------------------------------------------

class MaternalRiskEngine:
    """
    Core maternal risk assessment engine.

    Uses rule-based scoring as primary method with optional ML model overlay.
    Designed for African maternal health contexts with bias mitigation.
    """

    MODEL_VERSION = "1.0.0"
    MODEL_PATH = Path(__file__).parent / "models" / "risk_model.joblib"

    def __init__(self, language: str = "en") -> None:
        self.language = language
        self._ml_model = self._load_ml_model()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assess_risk(self, inp: RiskInput) -> RiskOutput:
        """
        Perform a full maternal risk assessment.

        Args:
            inp: RiskInput with all clinical and lifestyle data.

        Returns:
            RiskOutput with scores, explanations, and recommendations.
        """
        try:
            # 1. Condition-specific scores
            miscarriage_score = self._score_miscarriage(inp)
            preeclampsia_score = self._score_preeclampsia(inp)
            gd_score = self._score_gestational_diabetes(inp)
            anemia_score = self._score_anemia(inp)
            preterm_score = self._score_preterm_birth(inp)

            # 2. Emergency detection
            is_emergency, emergency_type = self._detect_emergency(inp)

            # 3. Overall score (weighted average)
            weights = [0.20, 0.30, 0.15, 0.15, 0.20]
            scores = [miscarriage_score, preeclampsia_score, gd_score,
                      anemia_score, preterm_score]
            overall_score = float(np.dot(weights, scores))

            # 4. ML model overlay (if available)
            ml_score, confidence = self._apply_ml_model(inp, overall_score)
            if ml_score is not None:
                overall_score = 0.6 * ml_score + 0.4 * overall_score
                confidence_score = confidence
            else:
                confidence_score = self._estimate_confidence(inp)

            if is_emergency:
                overall_score = max(overall_score, 0.85)

            # 5. Risk level
            overall_risk_level = self._score_to_level(overall_score, is_emergency)

            # 6. Feature importance / explanations
            risk_factors = self._build_risk_factors(inp, scores)
            protective_factors = self._build_protective_factors(inp)

            # 7. Recommendations
            recommendations = self._build_recommendations(
                inp, overall_risk_level, scores
            )
            immediate_actions = self._build_immediate_actions(
                inp, is_emergency, emergency_type, overall_risk_level
            )

            # 8. Follow-up interval
            next_assessment_days = self._next_assessment_days(
                overall_risk_level, inp.gestational_age_weeks
            )

            # 9. Bias notes
            bias_notes = self._bias_notes(inp)

            return RiskOutput(
                overall_risk_level=overall_risk_level,
                overall_risk_score=round(overall_score, 4),
                confidence_score=round(confidence_score, 4),
                miscarriage_risk_score=round(miscarriage_score, 4),
                preeclampsia_risk_score=round(preeclampsia_score, 4),
                gestational_diabetes_risk_score=round(gd_score, 4),
                anemia_risk_score=round(anemia_score, 4),
                preterm_birth_risk_score=round(preterm_score, 4),
                risk_factors=risk_factors,
                protective_factors=protective_factors,
                recommendations=recommendations,
                immediate_actions=immediate_actions,
                is_emergency=is_emergency,
                emergency_type=emergency_type,
                next_assessment_days=next_assessment_days,
                model_version=self.MODEL_VERSION,
                bias_notes=bias_notes,
            )
        except Exception as exc:
            logger.exception("Risk assessment failed: %s", exc)
            raise

    # ------------------------------------------------------------------
    # Condition-specific scoring
    # ------------------------------------------------------------------

    def _score_preeclampsia(self, inp: RiskInput) -> float:
        """
        Score preeclampsia risk.
        Criteria: BP >= 140/90 after 20 weeks, symptoms, history.
        """
        score = 0.0
        symptoms = {s.lower() for s in inp.reported_symptoms}

        # Blood pressure criteria
        if inp.systolic_bp >= 160 or inp.diastolic_bp >= 110:
            score += 0.50  # severe range
        elif inp.systolic_bp >= 140 or inp.diastolic_bp >= 90:
            score += 0.30  # hypertensive range
        elif inp.systolic_bp >= 130 or inp.diastolic_bp >= 80:
            score += 0.10  # elevated

        # Gestational age (preeclampsia after 20 weeks)
        if inp.gestational_age_weeks >= 20:
            score += 0.05
        else:
            score *= 0.3  # very unlikely before 20 weeks

        # Symptoms
        pe_symptom_count = len(symptoms & PREECLAMPSIA_SYMPTOMS)
        score += min(pe_symptom_count * 0.08, 0.24)

        # History
        if inp.previous_preeclampsia:
            score += 0.20
        if inp.is_multiple_pregnancy:
            score += 0.10
        if inp.age > 35:
            score += 0.05
        if inp.bmi > 30:
            score += 0.05
        if "diabetes" in " ".join(inp.pre_existing_conditions).lower():
            score += 0.05
        if "kidney" in " ".join(inp.pre_existing_conditions).lower():
            score += 0.05

        return min(score, 1.0)

    def _score_anemia(self, inp: RiskInput) -> float:
        """
        Score anemia risk.
        WHO criteria: Hb < 11 g/dL in pregnancy.
        """
        score = 0.0

        if inp.hemoglobin < 7.0:
            score = 0.95  # severe anemia
        elif inp.hemoglobin < 8.0:
            score = 0.80  # moderate-severe
        elif inp.hemoglobin < 10.0:
            score = 0.60  # moderate
        elif inp.hemoglobin < 11.0:
            score = 0.35  # mild
        elif inp.hemoglobin < 11.5:
            score = 0.15  # borderline

        # Modifiers
        if inp.nutrition_status in (NutritionStatus.POOR, NutritionStatus.FAIR):
            score += 0.10
        if inp.is_multiple_pregnancy:
            score += 0.08
        if inp.gestational_age_weeks > 28:
            score += 0.05  # higher demand in third trimester
        if "malaria" in " ".join(inp.pre_existing_conditions).lower():
            score += 0.10
        if "sickle_cell" in " ".join(inp.pre_existing_conditions).lower():
            score += 0.15

        return min(score, 1.0)

    def _score_gestational_diabetes(self, inp: RiskInput) -> float:
        """
        Score gestational diabetes risk.
        Criteria: fasting glucose > 92 mg/dL (IADPSG), risk factors.
        """
        score = 0.0

        # Glucose thresholds
        if inp.blood_glucose >= 200:
            score += 0.70  # overt diabetes
        elif inp.blood_glucose >= 140:
            score += 0.50  # GDM likely
        elif inp.blood_glucose >= 126:
            score += 0.35
        elif inp.blood_glucose >= 92:
            score += 0.20  # IADPSG threshold
        elif inp.blood_glucose >= 85:
            score += 0.08

        # Risk factors
        if inp.previous_gestational_diabetes:
            score += 0.25
        if inp.bmi >= 30:
            score += 0.10
        elif inp.bmi >= 25:
            score += 0.05
        if inp.age >= 35:
            score += 0.05
        if "diabetes" in " ".join(inp.pre_existing_conditions).lower():
            score += 0.15
        if "pcos" in " ".join(inp.pre_existing_conditions).lower():
            score += 0.08
        if inp.is_multiple_pregnancy:
            score += 0.05

        return min(score, 1.0)

    def _score_miscarriage(self, inp: RiskInput) -> float:
        """
        Score miscarriage / pregnancy loss risk.
        Most relevant in first trimester.
        """
        score = 0.0

        # Gestational age - highest risk in first trimester
        if inp.gestational_age_weeks <= 12:
            base = 0.15
        elif inp.gestational_age_weeks <= 20:
            base = 0.05
        else:
            base = 0.02
        score += base

        # Age
        if inp.age >= 40:
            score += 0.20
        elif inp.age >= 35:
            score += 0.10
        elif inp.age < 18:
            score += 0.08

        # History
        score += min(inp.previous_miscarriages * 0.12, 0.36)

        # Lifestyle
        if inp.smoking:
            score += 0.08
        if inp.alcohol_use:
            score += 0.10

        # Medical
        conditions_str = " ".join(inp.pre_existing_conditions).lower()
        if "antiphospholipid" in conditions_str:
            score += 0.20
        if "thyroid" in conditions_str:
            score += 0.08
        if "uterine" in conditions_str:
            score += 0.10

        # Symptoms
        symptoms = {s.lower() for s in inp.reported_symptoms}
        if "bleeding" in symptoms or "spotting" in symptoms:
            score += 0.15
        if "cramping" in symptoms:
            score += 0.08

        return min(score, 1.0)

    def _score_preterm_birth(self, inp: RiskInput) -> float:
        """
        Score preterm birth risk (delivery before 37 weeks).
        """
        score = 0.0

        # Only relevant after viability
        if inp.gestational_age_weeks < 16:
            return 0.05

        # History
        if inp.previous_preterm_birth:
            score += 0.30
        if inp.is_multiple_pregnancy:
            score += 0.25

        # Cervical / uterine
        conditions_str = " ".join(inp.pre_existing_conditions).lower()
        if "cervical_incompetence" in conditions_str or "short_cervix" in conditions_str:
            score += 0.20
        if "uterine" in conditions_str:
            score += 0.10

        # Infections
        if "uti" in conditions_str or "bacterial_vaginosis" in conditions_str:
            score += 0.10

        # Lifestyle
        if inp.smoking:
            score += 0.08
        if inp.stress_level >= 8:
            score += 0.08
        elif inp.stress_level >= 6:
            score += 0.04

        # Symptoms
        symptoms = {s.lower() for s in inp.reported_symptoms}
        if "contractions" in symptoms or "pelvic_pressure" in symptoms:
            score += 0.15
        if "watery_discharge" in symptoms:
            score += 0.10

        # Age
        if inp.age < 18:
            score += 0.08

        return min(score, 1.0)

    # ------------------------------------------------------------------
    # Emergency detection
    # ------------------------------------------------------------------

    def _detect_emergency(self, inp: RiskInput) -> Tuple[bool, Optional[str]]:
        """Detect life-threatening emergency conditions."""
        symptoms = {s.lower() for s in inp.reported_symptoms}

        # Severe hypertension / eclampsia
        if inp.systolic_bp >= 160 or inp.diastolic_bp >= 110:
            if symptoms & {"headache", "vision_changes", "seizure", "confusion"}:
                return True, "eclampsia_risk"
            return True, "severe_hypertension"

        # Eclampsia / seizure
        if "seizure" in symptoms or "loss_of_consciousness" in symptoms:
            return True, "eclampsia"

        # Hemorrhage
        if "heavy_bleeding" in symptoms:
            return True, "obstetric_hemorrhage"

        # Fetal distress
        if "no_fetal_movement" in symptoms and inp.gestational_age_weeks >= 24:
            return True, "fetal_distress"

        # Cord prolapse
        if "cord_prolapse" in symptoms:
            return True, "cord_prolapse"

        # Severe anemia
        if inp.hemoglobin < 7.0:
            return True, "severe_anemia"

        # Severe symptoms
        critical = {"chest_pain", "difficulty_breathing", "severe_abdominal_pain"}
        if symptoms & critical:
            return True, "critical_symptoms"

        # Sepsis indicators
        if "high_fever" in symptoms and "foul_smelling_discharge" in symptoms:
            return True, "possible_sepsis"

        return False, None

    # ------------------------------------------------------------------
    # ML model
    # ------------------------------------------------------------------

    def _load_ml_model(self) -> Optional[Any]:
        """Load ML model if available, otherwise return None for rule-based fallback."""
        try:
            import joblib  # type: ignore
            if self.MODEL_PATH.exists():
                model = joblib.load(self.MODEL_PATH)
                logger.info("ML model loaded from %s", self.MODEL_PATH)
                return model
        except ImportError:
            logger.warning("joblib not installed; using rule-based scoring only.")
        except Exception as exc:
            logger.warning("Could not load ML model: %s. Using rule-based fallback.", exc)
        return None

    def _apply_ml_model(
        self, inp: RiskInput, rule_score: float
    ) -> Tuple[Optional[float], float]:
        """Apply ML model if loaded. Returns (score, confidence) or (None, 0)."""
        if self._ml_model is None:
            return None, 0.0
        try:
            features = self._extract_features(inp)
            feature_array = np.array(features).reshape(1, -1)
            proba = self._ml_model.predict_proba(feature_array)[0]
            # Assume binary: index 1 = high risk
            score = float(proba[1]) if len(proba) > 1 else float(proba[0])
            confidence = float(np.max(proba))
            return score, confidence
        except Exception as exc:
            logger.warning("ML model inference failed: %s", exc)
            return None, 0.0

    def _extract_features(self, inp: RiskInput) -> List[float]:
        """Extract numerical feature vector from RiskInput."""
        conditions_str = " ".join(inp.pre_existing_conditions).lower()
        symptoms_str = " ".join(inp.reported_symptoms).lower()
        return [
            float(inp.age),
            float(inp.gestational_age_weeks),
            float(inp.systolic_bp),
            float(inp.diastolic_bp),
            float(inp.blood_glucose),
            float(inp.heart_rate),
            float(inp.hemoglobin),
            float(inp.bmi),
            float(inp.previous_miscarriages),
            float(inp.previous_preeclampsia),
            float(inp.previous_gestational_diabetes),
            float(inp.previous_preterm_birth),
            float(inp.is_multiple_pregnancy),
            float(inp.smoking),
            float(inp.alcohol_use),
            float(inp.stress_level),
            float(["poor", "fair", "good", "excellent"].index(inp.nutrition_status.value)),
            float("diabetes" in conditions_str),
            float("hypertension" in conditions_str),
            float("malaria" in conditions_str),
            float("sickle_cell" in conditions_str),
            float("bleeding" in symptoms_str or "spotting" in symptoms_str),
            float("headache" in symptoms_str),
            float("vision_changes" in symptoms_str),
            float("swelling" in symptoms_str),
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _score_to_level(self, score: float, is_emergency: bool) -> RiskLevel:
        if is_emergency or score >= 0.75:
            return RiskLevel.EMERGENCY if is_emergency else RiskLevel.HIGH
        if score >= 0.50:
            return RiskLevel.HIGH
        if score >= 0.25:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    def _estimate_confidence(self, inp: RiskInput) -> float:
        """Estimate confidence based on data completeness."""
        filled = sum([
            inp.systolic_bp > 0,
            inp.diastolic_bp > 0,
            inp.blood_glucose > 0,
            inp.hemoglobin > 0,
            inp.weight_kg > 0,
            inp.height_cm > 0,
        ])
        return 0.50 + (filled / 6) * 0.40

    def _build_risk_factors(
        self, inp: RiskInput, scores: List[float]
    ) -> List[Dict[str, Any]]:
        """Build SHAP-style feature importance list."""
        factors: List[Dict[str, Any]] = []

        if inp.systolic_bp >= 140 or inp.diastolic_bp >= 90:
            factors.append({
                "factor": "elevated_blood_pressure",
                "weight": 0.30,
                "description": f"Blood pressure {inp.systolic_bp}/{inp.diastolic_bp} mmHg is above normal range (120/80).",
                "is_modifiable": True,
            })
        if inp.hemoglobin < 11.0:
            factors.append({
                "factor": "low_hemoglobin",
                "weight": 0.20,
                "description": f"Hemoglobin {inp.hemoglobin} g/dL is below the pregnancy threshold of 11 g/dL.",
                "is_modifiable": True,
            })
        if inp.blood_glucose >= 92:
            factors.append({
                "factor": "elevated_blood_glucose",
                "weight": 0.20,
                "description": f"Fasting glucose {inp.blood_glucose} mg/dL exceeds the 92 mg/dL threshold.",
                "is_modifiable": True,
            })
        if inp.age >= 35:
            factors.append({
                "factor": "advanced_maternal_age",
                "weight": 0.10,
                "description": f"Age {inp.age} years is associated with increased obstetric risks.",
                "is_modifiable": False,
            })
        if inp.previous_preeclampsia:
            factors.append({
                "factor": "history_of_preeclampsia",
                "weight": 0.20,
                "description": "Previous preeclampsia significantly increases recurrence risk.",
                "is_modifiable": False,
            })
        if inp.smoking:
            factors.append({
                "factor": "smoking",
                "weight": 0.15,
                "description": "Smoking increases risk of preterm birth, low birth weight, and miscarriage.",
                "is_modifiable": True,
            })
        if inp.is_multiple_pregnancy:
            factors.append({
                "factor": "multiple_pregnancy",
                "weight": 0.15,
                "description": "Multiple pregnancy (twins/triplets) increases risk of preeclampsia and preterm birth.",
                "is_modifiable": False,
            })
        if inp.stress_level >= 7:
            factors.append({
                "factor": "high_stress",
                "weight": 0.08,
                "description": f"Stress level {inp.stress_level}/10 may contribute to preterm birth and poor outcomes.",
                "is_modifiable": True,
            })
        if inp.bmi >= 30:
            factors.append({
                "factor": "obesity",
                "weight": 0.10,
                "description": f"BMI {inp.bmi:.1f} kg/m2 increases risk of gestational diabetes and preeclampsia.",
                "is_modifiable": True,
            })

        return factors

    def _build_protective_factors(self, inp: RiskInput) -> List[str]:
        """Identify protective factors."""
        factors: List[str] = []
        if inp.hemoglobin >= 12.0:
            factors.append("Good hemoglobin levels reduce anemia risk.")
        if inp.systolic_bp < 120 and inp.diastolic_bp < 80:
            factors.append("Normal blood pressure is a strong protective factor.")
        if inp.blood_glucose < 92:
            factors.append("Normal fasting glucose reduces gestational diabetes risk.")
        if inp.nutrition_status in (NutritionStatus.GOOD, NutritionStatus.EXCELLENT):
            factors.append("Good nutritional status supports healthy pregnancy.")
        if not inp.smoking and not inp.alcohol_use:
            factors.append("Avoiding smoking and alcohol protects fetal development.")
        if inp.stress_level <= 4:
            factors.append("Low stress levels support healthy pregnancy outcomes.")
        if 18 <= inp.age <= 34:
            factors.append("Optimal maternal age range for pregnancy.")
        return factors

    def _build_recommendations(
        self,
        inp: RiskInput,
        risk_level: RiskLevel,
        scores: List[float],
    ) -> List[str]:
        """Build prioritized, localized recommendations."""
        lang = inp.language if inp.language in ("en", "sw", "fr", "ar") else "en"
        recs: List[str] = []

        def t(key: str) -> str:
            return RECOMMENDATIONS_I18N.get(key, {}).get(lang, RECOMMENDATIONS_I18N.get(key, {}).get("en", key))

        # Universal
        recs.append(t("attend_anc"))
        recs.append(t("hydration"))
        recs.append(t("nutrition"))

        # Condition-specific
        miscarriage_score, preeclampsia_score, gd_score, anemia_score, preterm_score = scores

        if preeclampsia_score >= 0.25:
            recs.append(t("monitor_bp"))
        if anemia_score >= 0.25:
            recs.append(t("iron_supplement"))
        if gd_score >= 0.25:
            recs.append(t("glucose_monitoring"))
        if inp.smoking:
            recs.append(t("stop_smoking"))
        if inp.stress_level >= 6:
            recs.append(t("mental_health"))

        recs.append(t("rest"))

        # Simplify for low literacy
        if inp.literacy_level == "low":
            recs = [r.split(".")[0] + "." for r in recs]

        return recs

    def _build_immediate_actions(
        self,
        inp: RiskInput,
        is_emergency: bool,
        emergency_type: Optional[str],
        risk_level: RiskLevel,
    ) -> List[str]:
        """Build immediate action list for high/emergency cases."""
        lang = inp.language if inp.language in ("en", "sw", "fr", "ar") else "en"
        actions: List[str] = []

        def t(key: str) -> str:
            return RECOMMENDATIONS_I18N.get(key, {}).get(lang, RECOMMENDATIONS_I18N.get(key, {}).get("en", key))

        if is_emergency:
            actions.append(t("emergency_visit"))
            if emergency_type == "eclampsia_risk":
                actions.append("Call emergency services immediately. Do not drive yourself.")
            elif emergency_type == "obstetric_hemorrhage":
                actions.append("Lie down, elevate legs, and call emergency services.")
            elif emergency_type == "fetal_distress":
                actions.append("Go to hospital immediately for fetal monitoring.")
            elif emergency_type == "severe_anemia":
                actions.append("Urgent blood transfusion may be required. Go to hospital now.")
        elif risk_level == RiskLevel.HIGH:
            actions.append("Contact your healthcare provider within 24 hours.")
            actions.append(t("monitor_bp"))

        return actions

    def _next_assessment_days(self, risk_level: RiskLevel, ga_weeks: int) -> int:
        """Determine days until next assessment based on risk level."""
        if risk_level == RiskLevel.EMERGENCY:
            return 0  # immediate
        if risk_level == RiskLevel.HIGH:
            return 3
        if risk_level == RiskLevel.MODERATE:
            return 7
        # Low risk - standard ANC schedule
        if ga_weeks < 28:
            return 28
        if ga_weeks < 36:
            return 14
        return 7

    def _bias_notes(self, inp: RiskInput) -> List[str]:
        """
        Add bias mitigation notes relevant to African populations.
        Acknowledges known model limitations.
        """
        notes: List[str] = []
        notes.append(
            "Risk thresholds are calibrated for sub-Saharan African populations "
            "where baseline hemoglobin and BP norms may differ from Western references."
        )
        if inp.age < 18:
            notes.append(
                "Adolescent pregnancy carries additional social and medical risks "
                "that may not be fully captured by clinical scores alone."
            )
        if "sickle_cell" in " ".join(inp.pre_existing_conditions).lower():
            notes.append(
                "Sickle cell disease prevalence is higher in African populations; "
                "standard anemia thresholds may underestimate severity."
            )
        return notes


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def assess_maternal_risk(
    age: int,
    gestational_age_weeks: int,
    systolic_bp: float,
    diastolic_bp: float,
    blood_glucose: float,
    heart_rate: float,
    hemoglobin: float,
    weight_kg: float,
    height_cm: float,
    **kwargs: Any,
) -> RiskOutput:
    """
    Convenience wrapper for quick risk assessment.

    Example:
        result = assess_maternal_risk(
            age=28, gestational_age_weeks=32,
            systolic_bp=145, diastolic_bp=95,
            blood_glucose=88, heart_rate=82,
            hemoglobin=10.2, weight_kg=68, height_cm=162,
            previous_preeclampsia=True,
        )
    """
    inp = RiskInput(
        age=age,
        gestational_age_weeks=gestational_age_weeks,
        systolic_bp=systolic_bp,
        diastolic_bp=diastolic_bp,
        blood_glucose=blood_glucose,
        heart_rate=heart_rate,
        hemoglobin=hemoglobin,
        weight_kg=weight_kg,
        height_cm=height_cm,
        **kwargs,
    )
    engine = MaternalRiskEngine(language=kwargs.get("language", "en"))
    return engine.assess_risk(inp)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json as _json

    sample = RiskInput(
        age=32,
        gestational_age_weeks=28,
        systolic_bp=148,
        diastolic_bp=96,
        blood_glucose=105,
        heart_rate=88,
        hemoglobin=9.8,
        weight_kg=72,
        height_cm=160,
        previous_preeclampsia=True,
        previous_miscarriages=1,
        reported_symptoms=["headache", "swelling_hands", "vision_changes"],
        language="en",
    )

    engine = MaternalRiskEngine()
    result = engine.assess_risk(sample)

    output = {
        "overall_risk_level": result.overall_risk_level.value,
        "overall_risk_score": result.overall_risk_score,
        "confidence_score": result.confidence_score,
        "is_emergency": result.is_emergency,
        "emergency_type": result.emergency_type,
        "preeclampsia_risk_score": result.preeclampsia_risk_score,
        "anemia_risk_score": result.anemia_risk_score,
        "recommendations": result.recommendations,
        "immediate_actions": result.immediate_actions,
        "risk_factors": result.risk_factors,
        "protective_factors": result.protective_factors,
        "next_assessment_days": result.next_assessment_days,
    }
    print(_json.dumps(output, indent=2, ensure_ascii=False))
