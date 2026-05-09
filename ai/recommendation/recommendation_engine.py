"""
MAMA-LENS AI - Personalized Care Recommendation Engine
Generates personalized maternal health recommendations based on
risk assessment, pregnancy stage, user profile, and local context.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RecommendationCategory(str, Enum):
    NUTRITION = "nutrition"
    EXERCISE = "exercise"
    ANC_VISIT = "anc_visit"
    MEDICATION = "medication"
    LIFESTYLE = "lifestyle"
    MENTAL_HEALTH = "mental_health"
    EDUCATION = "education"
    EMERGENCY_PREP = "emergency_prep"
    MONITORING = "monitoring"


class UrgencyLevel(str, Enum):
    IMMEDIATE = "immediate"    # Do now
    HIGH = "high"              # Within 24 hours
    MEDIUM = "medium"          # Within a week
    LOW = "low"                # General guidance
    INFORMATIONAL = "informational"


class AdherenceStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    OVERDUE = "overdue"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class UserProfile:
    """User profile for personalized recommendations."""
    user_id: str
    age: int
    gestational_age_weeks: int
    language: str = "en"
    literacy_level: str = "medium"
    location: str = ""
    risk_level: str = "low"
    risk_scores: Dict[str, float] = field(default_factory=dict)
    pre_existing_conditions: List[str] = field(default_factory=list)
    previous_pregnancies: int = 0
    is_multiple_pregnancy: bool = False
    has_partner_support: bool = True
    has_healthcare_access: bool = True
    income_level: str = "low"   # low / medium / high
    dietary_restrictions: List[str] = field(default_factory=list)
    completed_recommendations: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """A single personalized recommendation."""
    id: str
    category: RecommendationCategory
    urgency: UrgencyLevel
    title: str
    description: str
    action_steps: List[str]
    rationale: str
    due_date: Optional[str] = None
    frequency: Optional[str] = None   # e.g., "daily", "weekly"
    adherence_status: AdherenceStatus = AdherenceStatus.NOT_STARTED
    is_completed: bool = False
    local_resources: List[str] = field(default_factory=list)
    education_link: Optional[str] = None


@dataclass
class RecommendationPlan:
    """Complete personalized recommendation plan."""
    user_id: str
    gestational_age_weeks: int
    risk_level: str
    recommendations: List[Recommendation]
    weekly_education: str
    next_anc_date: Optional[str]
    emergency_contacts: List[str]
    adherence_summary: Dict[str, int]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    valid_until: str = field(
        default_factory=lambda: (datetime.utcnow() + timedelta(days=7)).isoformat()
    )


# ---------------------------------------------------------------------------
# African food database for nutrition recommendations
# ---------------------------------------------------------------------------

AFRICAN_FOODS: Dict[str, Dict[str, Any]] = {
    "iron_rich": {
        "foods": [
            "Beans (maharagwe)", "Lentils (dengu)", "Dark leafy greens (sukuma wiki, spinach)",
            "Liver (ini)", "Red meat (nyama nyekundu)", "Pumpkin seeds (mbegu za malenge)",
            "Moringa leaves (mchicha wa moringa)", "Amaranth (terere)",
            "Groundnuts (karanga)", "Millet (mtama)",
        ],
        "tip_en": "Eat iron-rich foods with vitamin C (tomatoes, oranges) to improve absorption. Avoid tea/coffee with meals.",
        "tip_sw": "Kula vyakula vyenye chuma pamoja na vitamini C (nyanya, machungwa) kuboresha unyonyaji. Epuka chai/kahawa wakati wa chakula.",
    },
    "folic_acid": {
        "foods": [
            "Dark green vegetables (spinach, kale, sukuma wiki)",
            "Beans and lentils", "Avocado (parachichi)", "Eggs (mayai)",
            "Fortified maize flour (unga wa mahindi ulioboreshwa)",
            "Groundnuts (karanga)", "Sunflower seeds",
        ],
        "tip_en": "Folic acid is critical in the first 12 weeks to prevent neural tube defects. Take supplements if prescribed.",
        "tip_sw": "Asidi ya foliki ni muhimu katika wiki 12 za kwanza kuzuia kasoro za bomba la neva.",
    },
    "protein": {
        "foods": [
            "Eggs (mayai)", "Fish (samaki) - tilapia, dagaa (sardines)",
            "Chicken (kuku)", "Beans (maharagwe)", "Lentils (dengu)",
            "Groundnuts (karanga)", "Milk (maziwa)", "Yogurt (mtindi)",
            "Soybean products (bidhaa za soya)", "Cowpeas (kunde)",
        ],
        "tip_en": "Aim for protein at every meal. Dried fish (dagaa) is affordable and nutritious.",
        "tip_sw": "Lenga protini kwa kila mlo. Dagaa ni ya bei nafuu na yenye lishe.",
    },
    "calcium": {
        "foods": [
            "Milk (maziwa)", "Yogurt (mtindi)", "Cheese (jibini)",
            "Dark leafy greens (mboga za majani)", "Sardines with bones (dagaa)",
            "Fortified soy milk", "Sesame seeds (mbegu za ufuta)",
            "Amaranth (terere)", "Moringa (mchicha wa moringa)",
        ],
        "tip_en": "Calcium is vital for baby's bone development. If dairy is expensive, dark greens and dagaa are great alternatives.",
        "tip_sw": "Kalsiamu ni muhimu kwa ukuaji wa mifupa ya mtoto. Mboga za majani na dagaa ni mbadala nzuri.",
    },
    "hydration": {
        "foods": [
            "Clean boiled water (maji safi yaliyochemshwa)",
            "Coconut water (maji ya nazi)", "Fresh fruit juices (juisi za matunda)",
            "Soup/broth (supu)", "Porridge (uji)",
        ],
        "tip_en": "Drink 8-10 glasses of clean water daily. Coconut water is excellent for hydration and electrolytes.",
        "tip_sw": "Kunywa glasi 8-10 za maji safi kila siku. Maji ya nazi ni bora kwa unyevu na elektroliti.",
    },
    "avoid": {
        "foods": [
            "Raw/undercooked meat and fish", "Unpasteurized milk",
            "Raw eggs", "High-mercury fish (shark, swordfish)",
            "Alcohol (pombe)", "Excessive caffeine (chai nyingi, kahawa nyingi)",
            "Unwashed fruits and vegetables", "Street food with unknown hygiene",
        ],
        "tip_en": "Avoid these foods to protect your baby from infections and toxins.",
        "tip_sw": "Epuka vyakula hivi kulinda mtoto wako dhidi ya maambukizi na sumu.",
    },
}

# ---------------------------------------------------------------------------
# ANC schedule (WHO 2016 - 8 contact model)
# ---------------------------------------------------------------------------

ANC_SCHEDULE: List[Dict[str, Any]] = [
    {"contact": 1, "weeks": 12, "purpose": "First contact: confirm pregnancy, blood tests, BP, weight, HIV test, iron/folic acid"},
    {"contact": 2, "weeks": 20, "purpose": "Anatomy scan, blood pressure, urine test, nutrition counseling"},
    {"contact": 3, "weeks": 26, "purpose": "Blood pressure, weight, fetal growth, glucose screening"},
    {"contact": 4, "weeks": 30, "purpose": "Blood pressure, fetal position, birth plan discussion"},
    {"contact": 5, "weeks": 34, "purpose": "Blood pressure, fetal wellbeing, preterm labor signs"},
    {"contact": 6, "weeks": 36, "purpose": "Blood pressure, fetal position, birth preparedness"},
    {"contact": 7, "weeks": 38, "purpose": "Blood pressure, fetal movement, labor signs"},
    {"contact": 8, "weeks": 40, "purpose": "Final assessment, birth plan confirmation, postpartum planning"},
]

# ---------------------------------------------------------------------------
# Exercise guidelines by trimester
# ---------------------------------------------------------------------------

EXERCISE_GUIDELINES: Dict[str, Dict[str, Any]] = {
    "first_trimester": {
        "weeks": (1, 13),
        "recommended": [
            "Walking (30 minutes daily)",
            "Gentle yoga or stretching",
            "Swimming (low impact)",
            "Pelvic floor exercises (Kegel exercises)",
        ],
        "avoid": [
            "High-impact sports", "Contact sports", "Exercises lying flat on back after week 12",
            "Activities with fall risk",
        ],
        "tip_en": "Exercise helps with nausea and fatigue. Start slowly if you were not active before pregnancy.",
        "tip_sw": "Mazoezi husaidia na kichefuchefu na uchovu. Anza polepole ikiwa hukuwa na mazoezi kabla ya ujauzito.",
    },
    "second_trimester": {
        "weeks": (14, 27),
        "recommended": [
            "Walking (30-45 minutes daily)",
            "Prenatal yoga", "Swimming", "Low-impact aerobics",
            "Pelvic floor exercises", "Gentle strength training",
        ],
        "avoid": [
            "Lying flat on back for extended periods",
            "High-altitude activities", "Scuba diving", "Contact sports",
        ],
        "tip_en": "Second trimester is often the most comfortable for exercise. Enjoy it!",
        "tip_sw": "Trimesta ya pili mara nyingi ni ya starehe zaidi kwa mazoezi. Furahia!",
    },
    "third_trimester": {
        "weeks": (28, 42),
        "recommended": [
            "Walking (20-30 minutes daily)",
            "Prenatal yoga", "Swimming", "Pelvic floor exercises",
            "Gentle stretching", "Birth preparation exercises",
        ],
        "avoid": [
            "Lying flat on back", "Heavy lifting", "High-impact activities",
            "Exercises that cause breathlessness",
        ],
        "tip_en": "Listen to your body. Rest when needed. Pelvic floor exercises prepare you for birth.",
        "tip_sw": "Sikiliza mwili wako. Pumzika unapohitajika. Mazoezi ya sakafu ya pelvic yanakuandaa kwa kuzaa.",
    },
}


# ---------------------------------------------------------------------------
# RecommendationEngine
# ---------------------------------------------------------------------------

class RecommendationEngine:
    """
    Generates personalized maternal health recommendations.

    Considers risk level, gestational age, user profile, local food options,
    literacy level, and adherence history to produce actionable guidance.
    """

    def generate_plan(self, profile: UserProfile) -> RecommendationPlan:
        """
        Generate a complete personalized recommendation plan.

        Args:
            profile: UserProfile with all user data.

        Returns:
            RecommendationPlan with prioritized recommendations.
        """
        recommendations: List[Recommendation] = []

        # 1. Nutrition recommendations
        recommendations.extend(self._nutrition_recommendations(profile))

        # 2. Exercise recommendations
        recommendations.extend(self._exercise_recommendations(profile))

        # 3. ANC visit recommendations
        recommendations.extend(self._anc_recommendations(profile))

        # 4. Medication recommendations
        recommendations.extend(self._medication_recommendations(profile))

        # 5. Lifestyle recommendations
        recommendations.extend(self._lifestyle_recommendations(profile))

        # 6. Mental health recommendations
        recommendations.extend(self._mental_health_recommendations(profile))

        # 7. Monitoring recommendations
        recommendations.extend(self._monitoring_recommendations(profile))

        # 8. Emergency preparedness
        recommendations.extend(self._emergency_prep_recommendations(profile))

        # 9. Sort by urgency
        urgency_order = {
            UrgencyLevel.IMMEDIATE: 0,
            UrgencyLevel.HIGH: 1,
            UrgencyLevel.MEDIUM: 2,
            UrgencyLevel.LOW: 3,
            UrgencyLevel.INFORMATIONAL: 4,
        }
        recommendations.sort(key=lambda r: urgency_order.get(r.urgency, 5))

        # 10. Weekly education
        weekly_education = self._get_weekly_education(
            profile.gestational_age_weeks, profile.language
        )

        # 11. Next ANC date
        next_anc_date = self._get_next_anc_date(profile.gestational_age_weeks)

        # 12. Emergency contacts
        emergency_contacts = self._get_emergency_contacts(profile)

        # 13. Adherence summary
        adherence_summary = self._calculate_adherence(
            recommendations, profile.completed_recommendations
        )

        return RecommendationPlan(
            user_id=profile.user_id,
            gestational_age_weeks=profile.gestational_age_weeks,
            risk_level=profile.risk_level,
            recommendations=recommendations,
            weekly_education=weekly_education,
            next_anc_date=next_anc_date,
            emergency_contacts=emergency_contacts,
            adherence_summary=adherence_summary,
        )

    def update_adherence(
        self,
        plan: RecommendationPlan,
        recommendation_id: str,
        status: AdherenceStatus,
    ) -> RecommendationPlan:
        """Update adherence status for a recommendation."""
        for rec in plan.recommendations:
            if rec.id == recommendation_id:
                rec.adherence_status = status
                rec.is_completed = status == AdherenceStatus.COMPLETED
                break
        plan.adherence_summary = self._calculate_adherence(
            plan.recommendations,
            [r.id for r in plan.recommendations if r.is_completed],
        )
        return plan

    # ------------------------------------------------------------------
    # Nutrition
    # ------------------------------------------------------------------

    def _nutrition_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        recs: List[Recommendation] = []
        lang = profile.language
        ga = profile.gestational_age_weeks

        # Iron / anemia
        anemia_score = profile.risk_scores.get("anemia_risk_score", 0)
        if anemia_score >= 0.25 or "anemia" in " ".join(profile.pre_existing_conditions).lower():
            iron_foods = AFRICAN_FOODS["iron_rich"]["foods"][:5]
            tip = AFRICAN_FOODS["iron_rich"].get(f"tip_{lang}", AFRICAN_FOODS["iron_rich"]["tip_en"])
            recs.append(Recommendation(
                id="nutrition_iron",
                category=RecommendationCategory.NUTRITION,
                urgency=UrgencyLevel.HIGH if anemia_score >= 0.50 else UrgencyLevel.MEDIUM,
                title="Increase Iron-Rich Foods" if lang == "en" else "Ongeza Vyakula Vyenye Chuma",
                description=f"Your hemoglobin levels suggest you need more iron. {tip}",
                action_steps=[
                    f"Include these iron-rich foods daily: {', '.join(iron_foods[:3])}",
                    "Eat with vitamin C sources (tomatoes, oranges) to boost absorption",
                    "Take iron supplements as prescribed by your healthcare provider",
                    "Avoid tea and coffee within 1 hour of meals",
                ],
                rationale="Iron deficiency anemia is common in pregnancy and can cause fatigue, preterm birth, and low birth weight.",
                frequency="daily",
            ))

        # Folic acid (critical in first trimester)
        if ga <= 16:
            recs.append(Recommendation(
                id="nutrition_folic",
                category=RecommendationCategory.NUTRITION,
                urgency=UrgencyLevel.HIGH if ga <= 12 else UrgencyLevel.MEDIUM,
                title="Folic Acid Intake" if lang == "en" else "Ulaji wa Asidi ya Foliki",
                description=AFRICAN_FOODS["folic_acid"].get(f"tip_{lang}", AFRICAN_FOODS["folic_acid"]["tip_en"]),
                action_steps=[
                    "Take folic acid supplement (400-800 mcg daily) as prescribed",
                    f"Eat folic acid-rich foods: {', '.join(AFRICAN_FOODS['folic_acid']['foods'][:3])}",
                    "Continue until at least week 12",
                ],
                rationale="Folic acid prevents neural tube defects in the first 12 weeks.",
                frequency="daily",
            ))

        # General nutrition
        protein_foods = AFRICAN_FOODS["protein"]["foods"][:4]
        recs.append(Recommendation(
            id="nutrition_balanced",
            category=RecommendationCategory.NUTRITION,
            urgency=UrgencyLevel.LOW,
            title="Balanced Pregnancy Diet" if lang == "en" else "Lishe Bora ya Ujauzito",
            description="A balanced diet supports your baby's growth and your health.",
            action_steps=[
                f"Protein sources: {', '.join(protein_foods)}",
                f"Calcium sources: {', '.join(AFRICAN_FOODS['calcium']['foods'][:3])}",
                AFRICAN_FOODS["hydration"].get(f"tip_{lang}", AFRICAN_FOODS["hydration"]["tip_en"]),
                f"Foods to avoid: {', '.join(AFRICAN_FOODS['avoid']['foods'][:3])}",
            ],
            rationale="Adequate nutrition reduces risk of complications and supports fetal development.",
            frequency="daily",
        ))

        # Gestational diabetes nutrition
        gd_score = profile.risk_scores.get("gestational_diabetes_risk_score", 0)
        if gd_score >= 0.25:
            recs.append(Recommendation(
                id="nutrition_gd",
                category=RecommendationCategory.NUTRITION,
                urgency=UrgencyLevel.HIGH,
                title="Gestational Diabetes Diet" if lang == "en" else "Lishe ya Kisukari cha Ujauzito",
                description="Your glucose levels require dietary management.",
                action_steps=[
                    "Eat small, frequent meals (5-6 times daily)",
                    "Choose complex carbohydrates: whole grains, legumes, vegetables",
                    "Avoid sugary drinks, white bread, white rice in large portions",
                    "Monitor blood glucose as directed by your healthcare provider",
                    "Pair carbohydrates with protein at every meal",
                ],
                rationale="Dietary management is the first-line treatment for gestational diabetes.",
                frequency="daily",
            ))

        return recs

    # ------------------------------------------------------------------
    # Exercise
    # ------------------------------------------------------------------

    def _exercise_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        ga = profile.gestational_age_weeks
        lang = profile.language

        if ga <= 13:
            trimester_key = "first_trimester"
        elif ga <= 27:
            trimester_key = "second_trimester"
        else:
            trimester_key = "third_trimester"

        guidelines = EXERCISE_GUIDELINES[trimester_key]
        tip = guidelines.get(f"tip_{lang}", guidelines["tip_en"])

        return [Recommendation(
            id=f"exercise_{trimester_key}",
            category=RecommendationCategory.EXERCISE,
            urgency=UrgencyLevel.LOW,
            title=f"Exercise Guide - Week {ga}" if lang == "en" else f"Mwongozo wa Mazoezi - Wiki {ga}",
            description=tip,
            action_steps=[
                f"Recommended: {', '.join(guidelines['recommended'][:3])}",
                f"Avoid: {', '.join(guidelines['avoid'][:2])}",
                "Stop exercising if you feel pain, dizziness, or shortness of breath",
                "Always warm up and cool down",
            ],
            rationale="Regular moderate exercise reduces risk of gestational diabetes, preeclampsia, and excessive weight gain.",
            frequency="daily",
        )]

    # ------------------------------------------------------------------
    # ANC visits
    # ------------------------------------------------------------------

    def _anc_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        ga = profile.gestational_age_weeks
        lang = profile.language
        recs: List[Recommendation] = []

        # Find upcoming ANC contacts
        upcoming = [c for c in ANC_SCHEDULE if c["weeks"] >= ga][:2]

        for contact in upcoming:
            weeks_until = contact["weeks"] - ga
            urgency = UrgencyLevel.HIGH if weeks_until <= 2 else UrgencyLevel.MEDIUM

            recs.append(Recommendation(
                id=f"anc_contact_{contact['contact']}",
                category=RecommendationCategory.ANC_VISIT,
                urgency=urgency,
                title=f"ANC Visit {contact['contact']} (Week {contact['weeks']})" if lang == "en"
                      else f"Ziara ya Kliniki {contact['contact']} (Wiki {contact['weeks']})",
                description=contact["purpose"],
                action_steps=[
                    f"Schedule your visit at week {contact['weeks']}",
                    "Bring your ANC card/booklet",
                    "Prepare questions for your healthcare provider",
                    "Bring a support person if possible",
                ],
                rationale="Regular ANC visits detect complications early and save lives.",
                due_date=(datetime.utcnow() + timedelta(weeks=weeks_until)).isoformat(),
            ))

        # High-risk: more frequent visits
        if profile.risk_level in ("high", "emergency"):
            recs.insert(0, Recommendation(
                id="anc_high_risk",
                category=RecommendationCategory.ANC_VISIT,
                urgency=UrgencyLevel.HIGH,
                title="Urgent: Contact Healthcare Provider" if lang == "en"
                      else "Haraka: Wasiliana na Mtoa Huduma wa Afya",
                description="Your risk assessment indicates you need more frequent monitoring.",
                action_steps=[
                    "Contact your healthcare provider within 24-48 hours",
                    "Do not wait for your scheduled visit if symptoms worsen",
                    "Monitor blood pressure daily if possible",
                ],
                rationale="High-risk pregnancies require closer monitoring to prevent complications.",
                due_date=datetime.utcnow().isoformat(),
            ))

        return recs

    # ------------------------------------------------------------------
    # Medications
    # ------------------------------------------------------------------

    def _medication_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        recs: List[Recommendation] = []
        lang = profile.language
        ga = profile.gestational_age_weeks

        # Iron + folic acid (universal)
        recs.append(Recommendation(
            id="medication_iron_folic",
            category=RecommendationCategory.MEDICATION,
            urgency=UrgencyLevel.MEDIUM,
            title="Iron and Folic Acid Supplements" if lang == "en"
                  else "Virutubisho vya Chuma na Asidi ya Foliki",
            description="Take iron (60mg) and folic acid (400mcg) daily as prescribed.",
            action_steps=[
                "Take iron tablet daily, preferably on empty stomach or with vitamin C",
                "Take folic acid daily throughout pregnancy",
                "If iron causes constipation, increase water and fiber intake",
                "Do not take iron with tea, coffee, or calcium supplements",
            ],
            rationale="Iron prevents anemia; folic acid prevents neural tube defects.",
            frequency="daily",
        ))

        # Malaria prophylaxis (endemic regions)
        if "malaria" in profile.location.lower() or "kenya" in profile.location.lower() \
                or "tanzania" in profile.location.lower() or "uganda" in profile.location.lower():
            if ga >= 16:
                recs.append(Recommendation(
                    id="medication_ipt",
                    category=RecommendationCategory.MEDICATION,
                    urgency=UrgencyLevel.MEDIUM,
                    title="Malaria Prevention (IPTp)" if lang == "en"
                          else "Kuzuia Malaria (IPTp)",
                    description="Intermittent preventive treatment for malaria in pregnancy.",
                    action_steps=[
                        "Ask your healthcare provider about IPTp-SP (sulfadoxine-pyrimethamine)",
                        "This is given at ANC visits from week 16 onwards",
                        "Sleep under an insecticide-treated bed net every night",
                        "Wear long sleeves in the evening to prevent mosquito bites",
                    ],
                    rationale="Malaria in pregnancy causes anemia, low birth weight, and maternal death.",
                    frequency="at_anc_visits",
                ))

        return recs

    # ------------------------------------------------------------------
    # Lifestyle
    # ------------------------------------------------------------------

    def _lifestyle_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        recs: List[Recommendation] = []
        lang = profile.language

        # Sleep
        recs.append(Recommendation(
            id="lifestyle_sleep",
            category=RecommendationCategory.LIFESTYLE,
            urgency=UrgencyLevel.LOW,
            title="Rest and Sleep" if lang == "en" else "Pumzika na Kulala",
            description="Adequate rest is essential during pregnancy.",
            action_steps=[
                "Aim for 8-9 hours of sleep per night",
                "Sleep on your left side after week 20 to improve blood flow",
                "Use pillows for support between knees and under belly",
                "Take short rest breaks during the day if needed",
            ],
            rationale="Poor sleep is linked to preeclampsia, gestational diabetes, and preterm birth.",
            frequency="daily",
        ))

        # Stress management
        recs.append(Recommendation(
            id="lifestyle_stress",
            category=RecommendationCategory.LIFESTYLE,
            urgency=UrgencyLevel.LOW,
            title="Stress Management" if lang == "en" else "Kudhibiti Msongo wa Mawazo",
            description="Managing stress protects both you and your baby.",
            action_steps=[
                "Practice deep breathing exercises for 10 minutes daily",
                "Share your worries with a trusted person",
                "Reduce workload where possible",
                "Engage in enjoyable activities",
                "Join a pregnancy support group if available",
            ],
            rationale="Chronic stress increases risk of preterm birth and low birth weight.",
            frequency="daily",
        ))

        # Hygiene
        recs.append(Recommendation(
            id="lifestyle_hygiene",
            category=RecommendationCategory.LIFESTYLE,
            urgency=UrgencyLevel.LOW,
            title="Personal Hygiene" if lang == "en" else "Usafi wa Kibinafsi",
            description="Good hygiene prevents infections during pregnancy.",
            action_steps=[
                "Wash hands frequently with soap and water",
                "Drink only clean, boiled or treated water",
                "Wash fruits and vegetables before eating",
                "Maintain dental hygiene - brush twice daily",
                "Avoid contact with people who are sick",
            ],
            rationale="Infections during pregnancy can cause preterm birth and other complications.",
            frequency="daily",
        ))

        return recs

    # ------------------------------------------------------------------
    # Mental health
    # ------------------------------------------------------------------

    def _mental_health_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        recs: List[Recommendation] = []
        lang = profile.language

        recs.append(Recommendation(
            id="mental_health_support",
            category=RecommendationCategory.MENTAL_HEALTH,
            urgency=UrgencyLevel.LOW,
            title="Emotional Wellbeing" if lang == "en" else "Afya ya Kihisia",
            description="Your emotional health is as important as your physical health.",
            action_steps=[
                "Talk to your partner, family, or friends about your feelings",
                "It is normal to feel anxious or overwhelmed - you are not alone",
                "If you feel persistently sad or hopeless, tell your healthcare provider",
                "Practice self-care: rest, gentle exercise, enjoyable activities",
            ],
            rationale="Perinatal depression affects 1 in 5 women and is treatable.",
            frequency="weekly",
        ))

        if not profile.has_partner_support:
            recs.append(Recommendation(
                id="mental_health_social",
                category=RecommendationCategory.MENTAL_HEALTH,
                urgency=UrgencyLevel.MEDIUM,
                title="Build Your Support Network" if lang == "en"
                      else "Jenga Mtandao Wako wa Msaada",
                description="Having support during pregnancy improves outcomes.",
                action_steps=[
                    "Connect with other pregnant women in your community",
                    "Ask a trusted family member to accompany you to ANC visits",
                    "Contact community health workers for home visits",
                    "Reach out to local women's groups or church/mosque groups",
                ],
                rationale="Social support reduces depression risk and improves birth outcomes.",
                frequency="weekly",
            ))

        return recs

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    def _monitoring_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        recs: List[Recommendation] = []
        lang = profile.language
        ga = profile.gestational_age_weeks

        # Blood pressure monitoring for high-risk
        pe_score = profile.risk_scores.get("preeclampsia_risk_score", 0)
        if pe_score >= 0.25 or profile.risk_level in ("high", "emergency"):
            recs.append(Recommendation(
                id="monitoring_bp",
                category=RecommendationCategory.MONITORING,
                urgency=UrgencyLevel.HIGH,
                title="Daily Blood Pressure Monitoring" if lang == "en"
                      else "Kupima Shinikizo la Damu Kila Siku",
                description="Monitor your blood pressure daily and record readings.",
                action_steps=[
                    "Measure BP at the same time each day (morning preferred)",
                    "Sit quietly for 5 minutes before measuring",
                    "Record date, time, and reading in your ANC card",
                    "Go to hospital immediately if BP >= 140/90 mmHg",
                    "Watch for: severe headache, vision changes, swelling of face/hands",
                ],
                rationale="Early detection of rising BP prevents eclampsia and maternal death.",
                frequency="daily",
            ))

        # Fetal movement counting (after 28 weeks)
        if ga >= 28:
            recs.append(Recommendation(
                id="monitoring_fetal_movement",
                category=RecommendationCategory.MONITORING,
                urgency=UrgencyLevel.MEDIUM,
                title="Daily Fetal Movement Count" if lang == "en"
                      else "Kuhesabu Mwendo wa Mtoto Kila Siku",
                description="Count your baby's movements daily to ensure wellbeing.",
                action_steps=[
                    "Choose a time when baby is usually active (after meals)",
                    "Lie on your left side and count movements",
                    "You should feel at least 10 movements in 2 hours",
                    "If fewer than 10 movements in 2 hours, go to hospital immediately",
                    "Record counts in a kick count chart",
                ],
                rationale="Reduced fetal movement can indicate fetal distress.",
                frequency="daily",
            ))

        return recs

    # ------------------------------------------------------------------
    # Emergency preparedness
    # ------------------------------------------------------------------

    def _emergency_prep_recommendations(
        self, profile: UserProfile
    ) -> List[Recommendation]:
        lang = profile.language
        ga = profile.gestational_age_weeks

        if ga < 28:
            return []

        return [Recommendation(
            id="emergency_prep_birth",
            category=RecommendationCategory.EMERGENCY_PREP,
            urgency=UrgencyLevel.MEDIUM,
            title="Birth Preparedness Plan" if lang == "en"
                  else "Mpango wa Kujiandaa kwa Kuzaa",
            description="Prepare for birth to avoid delays that can cost lives.",
            action_steps=[
                "Identify the nearest health facility with maternity services",
                "Arrange transport to the facility in advance",
                "Save emergency contact numbers (facility, community health worker)",
                "Prepare a birth bag: ANC card, clean clothes, sanitary pads, baby clothes",
                "Identify a birth companion who will stay with you",
                "Save money for birth costs and emergencies",
                "Know the danger signs: heavy bleeding, severe headache, no fetal movement",
            ],
            rationale="Birth preparedness reduces the three delays that cause maternal death.",
            frequency="once",
        )]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_weekly_education(self, ga_weeks: int, language: str) -> str:
        """Get week-specific education content."""
        from ai.nlp.conversation_ai import WEEKLY_EDUCATION  # type: ignore
        try:
            available = sorted(WEEKLY_EDUCATION.keys())
            closest = min(available, key=lambda w: abs(w - ga_weeks))
            content = WEEKLY_EDUCATION.get(closest, {})
            return content.get(language, content.get("en", f"Week {ga_weeks} of your pregnancy journey."))
        except ImportError:
            return f"Week {ga_weeks}: Continue attending your ANC visits and taking your supplements."

    def _get_next_anc_date(self, ga_weeks: int) -> Optional[str]:
        """Calculate next ANC visit date."""
        upcoming = [c for c in ANC_SCHEDULE if c["weeks"] > ga_weeks]
        if not upcoming:
            return None
        next_contact = upcoming[0]
        weeks_until = next_contact["weeks"] - ga_weeks
        next_date = datetime.utcnow() + timedelta(weeks=weeks_until)
        return next_date.strftime("%Y-%m-%d")

    def _get_emergency_contacts(self, profile: UserProfile) -> List[str]:
        """Return emergency contact list."""
        contacts = [
            "Nearest health facility",
            "Community health worker",
            "Emergency services: 999 / 112",
        ]
        if "kenya" in profile.location.lower():
            contacts.append("Kenya Emergency: 999 / 0800 720 999")
        elif "tanzania" in profile.location.lower():
            contacts.append("Tanzania Emergency: 112")
        elif "uganda" in profile.location.lower():
            contacts.append("Uganda Emergency: 999 / 112")
        return contacts

    def _calculate_adherence(
        self,
        recommendations: List[Recommendation],
        completed_ids: List[str],
    ) -> Dict[str, int]:
        """Calculate adherence statistics."""
        total = len(recommendations)
        completed = sum(1 for r in recommendations if r.id in completed_ids or r.is_completed)
        overdue = sum(
            1 for r in recommendations
            if r.due_date and datetime.fromisoformat(r.due_date) < datetime.utcnow()
            and not r.is_completed
        )
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed - overdue,
            "overdue": overdue,
            "adherence_rate": round(completed / total * 100) if total > 0 else 0,
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def generate_recommendations(
    user_id: str,
    age: int,
    gestational_age_weeks: int,
    risk_level: str = "low",
    risk_scores: Optional[Dict[str, float]] = None,
    language: str = "en",
    **kwargs: Any,
) -> RecommendationPlan:
    """
    Quick recommendation generation wrapper.

    Example:
        plan = generate_recommendations(
            user_id="user_123",
            age=28,
            gestational_age_weeks=32,
            risk_level="moderate",
            risk_scores={"anemia_risk_score": 0.45, "preeclampsia_risk_score": 0.30},
            language="sw",
        )
    """
    profile = UserProfile(
        user_id=user_id,
        age=age,
        gestational_age_weeks=gestational_age_weeks,
        risk_level=risk_level,
        risk_scores=risk_scores or {},
        language=language,
        **kwargs,
    )
    engine = RecommendationEngine()
    return engine.generate_plan(profile)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json as _json

    profile = UserProfile(
        user_id="demo_user_001",
        age=28,
        gestational_age_weeks=32,
        language="en",
        literacy_level="medium",
        location="Nairobi, Kenya",
        risk_level="moderate",
        risk_scores={
            "anemia_risk_score": 0.45,
            "preeclampsia_risk_score": 0.30,
            "gestational_diabetes_risk_score": 0.15,
        },
        has_partner_support=True,
        income_level="low",
    )

    engine = RecommendationEngine()
    plan = engine.generate_plan(profile)

    print(f"\n=== Recommendation Plan for User {profile.user_id} ===")
    print(f"Gestational Age: {plan.gestational_age_weeks} weeks")
    print(f"Risk Level: {plan.risk_level}")
    print(f"Total Recommendations: {len(plan.recommendations)}")
    print(f"Next ANC Date: {plan.next_anc_date}")
    print(f"\nWeekly Education:\n{plan.weekly_education}")
    print(f"\nAdherence Summary: {plan.adherence_summary}")
    print(f"\nTop 5 Recommendations:")
    for i, rec in enumerate(plan.recommendations[:5], 1):
        print(f"\n{i}. [{rec.urgency.value.upper()}] {rec.title}")
        print(f"   Category: {rec.category.value}")
        print(f"   {rec.description[:100]}...")
        print(f"   Steps: {rec.action_steps[0]}")
