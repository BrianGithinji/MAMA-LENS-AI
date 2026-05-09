"""
MAMA-LENS AI - Emotion Detection for Maternal Mental Health
Detects emotional states, depression risk, grief, and crisis signals
from text input. Implements EPDS scoring and compassionate escalation.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PrimaryEmotion(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANXIETY = "anxiety"
    FEAR = "fear"
    ANGER = "anger"
    GRIEF = "grief"
    HOPELESSNESS = "hopelessness"
    NEUTRAL = "neutral"
    CONFUSION = "confusion"
    LONELINESS = "loneliness"


class ResponseTone(str, Enum):
    WARM_SUPPORTIVE = "warm_supportive"
    CALM_REASSURING = "calm_reassuring"
    URGENT_CARING = "urgent_caring"
    EMPATHETIC_GRIEF = "empathetic_grief"
    PROFESSIONAL_CLINICAL = "professional_clinical"
    CRISIS_IMMEDIATE = "crisis_immediate"


# ---------------------------------------------------------------------------
# Input / Output models
# ---------------------------------------------------------------------------

@dataclass
class AudioFeatures:
    """Optional audio-derived features for multimodal emotion detection."""
    pitch_mean: float = 0.0
    pitch_variance: float = 0.0
    speech_rate: float = 0.0       # words per minute
    pause_frequency: float = 0.0   # pauses per minute
    energy_mean: float = 0.0
    tremor_detected: bool = False


@dataclass
class EmotionInput:
    """Input for emotion detection."""
    text: str
    audio_features: Optional[AudioFeatures] = None
    context: str = ""              # e.g., "post_miscarriage", "third_trimester"
    language: str = "en"
    session_history: List[str] = field(default_factory=list)
    epds_responses: Optional[List[int]] = None  # 10 EPDS items, scored 0-3


@dataclass
class EmotionOutput:
    """Complete emotion analysis output."""
    primary_emotion: PrimaryEmotion
    secondary_emotions: List[str]
    distress_level: float          # 0-1
    grief_indicators: List[str]
    depression_risk: float         # 0-1
    epds_score: Optional[int]      # 0-30 if EPDS provided
    epds_risk_level: Optional[str]
    requires_immediate_support: bool
    recommended_response_tone: ResponseTone
    crisis_detected: bool
    crisis_type: Optional[str]
    compassionate_response: str
    escalation_message: Optional[str]
    support_resources: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ---------------------------------------------------------------------------
# Keyword patterns
# ---------------------------------------------------------------------------

CRISIS_PATTERNS = [
    r"\b(kill\s+myself|end\s+my\s+life|want\s+to\s+die|suicid|self.harm|hurt\s+myself)\b",
    r"\b(no\s+reason\s+to\s+live|better\s+off\s+dead|can.t\s+go\s+on)\b",
    r"\b(overdose|cut\s+myself|jump|hang\s+myself)\b",
    r"\b(nobody\s+cares|completely\s+alone|no\s+hope)\b",
]

GRIEF_PATTERNS = [
    r"\b(lost\s+(my\s+)?(baby|child|pregnancy)|miscarriage|stillbirth|baby\s+died)\b",
    r"\b(empty\s+womb|never\s+hold|gone\s+forever|why\s+my\s+baby)\b",
    r"\b(grieving|mourning|heartbroken|devastated)\b",
    r"\b(angel\s+baby|heaven|memorial)\b",
]

ANXIETY_PATTERNS = [
    r"\b(worried|anxious|scared|terrified|panic|nervous|afraid)\b",
    r"\b(can.t\s+sleep|nightmares|racing\s+heart|chest\s+tight)\b",
    r"\b(what\s+if|something\s+wrong|baby\s+okay|normal)\b",
    r"\b(overwhelmed|too\s+much|can.t\s+cope|falling\s+apart)\b",
]

DEPRESSION_PATTERNS = [
    r"\b(hopeless|worthless|useless|failure|bad\s+mother)\b",
    r"\b(can.t\s+feel|numb|empty|hollow|disconnected)\b",
    r"\b(don.t\s+care|nothing\s+matters|pointless|meaningless)\b",
    r"\b(crying\s+all\s+day|can.t\s+stop\s+crying|tears)\b",
    r"\b(not\s+bonding|don.t\s+love\s+baby|resent|regret\s+pregnancy)\b",
]

JOY_PATTERNS = [
    r"\b(happy|excited|grateful|blessed|wonderful|amazing|love)\b",
    r"\b(can.t\s+wait|so\s+ready|thrilled|overjoyed|fantastic)\b",
    r"\b(feeling\s+good|doing\s+well|great|positive)\b",
]

ANGER_PATTERNS = [
    r"\b(angry|furious|rage|frustrated|irritated|annoyed)\b",
    r"\b(unfair|not\s+fair|why\s+me|hate|resent)\b",
]

LONELINESS_PATTERNS = [
    r"\b(alone|lonely|isolated|no\s+one|nobody|no\s+support)\b",
    r"\b(husband\s+(left|gone|absent)|no\s+family|far\s+from\s+home)\b",
]

# ---------------------------------------------------------------------------
# EPDS (Edinburgh Postnatal Depression Scale)
# ---------------------------------------------------------------------------

EPDS_QUESTIONS = [
    "I have been able to laugh and see the funny side of things",
    "I have looked forward with enjoyment to things",
    "I have blamed myself unnecessarily when things went wrong",
    "I have been anxious or worried for no good reason",
    "I have felt scared or panicky for no very good reason",
    "Things have been getting on top of me",
    "I have been so unhappy that I have had difficulty sleeping",
    "I have felt sad or miserable",
    "I have been so unhappy that I have been crying",
    "The thought of harming myself has occurred to me",
]

# Items 3-10 are reverse-scored in standard EPDS
EPDS_REVERSE_ITEMS = {0, 1}  # items 1 and 2 (0-indexed) are forward-scored


def score_epds(responses: List[int]) -> Tuple[int, str]:
    """
    Score Edinburgh Postnatal Depression Scale.

    Args:
        responses: List of 10 integers, each 0-3.

    Returns:
        (total_score, risk_level)
    """
    if len(responses) != 10:
        raise ValueError("EPDS requires exactly 10 responses (0-3 each).")

    # Items 1-2 (index 0-1): scored 0,1,2,3 (as given)
    # Items 3-10 (index 2-9): scored 3,2,1,0 (reversed)
    total = 0
    for i, resp in enumerate(responses):
        if i in EPDS_REVERSE_ITEMS:
            total += resp
        else:
            total += (3 - resp)

    if total >= 13:
        risk_level = "high"
    elif total >= 10:
        risk_level = "moderate"
    elif total >= 7:
        risk_level = "mild"
    else:
        risk_level = "low"

    return total, risk_level


# ---------------------------------------------------------------------------
# Support resources
# ---------------------------------------------------------------------------

SUPPORT_RESOURCES: Dict[str, List[str]] = {
    "en": [
        "Talk to your midwife or healthcare provider about how you are feeling.",
        "Contact a trusted family member or friend for support.",
        "Africa Mental Health Foundation: +254 722 178 177",
        "Befrienders Kenya (crisis line): +254 722 178 177",
        "WHO mhGAP mental health resources: www.who.int/mental_health",
    ],
    "sw": [
        "Zungumza na mkunga wako au mtoa huduma wa afya kuhusu hisia zako.",
        "Wasiliana na mwanafamilia au rafiki unayemwamini kwa msaada.",
        "Mstari wa msaada wa afya ya akili: +254 722 178 177",
    ],
    "fr": [
        "Parlez a votre sage-femme ou prestataire de soins de sante de vos sentiments.",
        "Contactez un membre de la famille ou un ami de confiance pour obtenir du soutien.",
        "Ligne d aide en sante mentale: +254 722 178 177",
    ],
}

COMPASSIONATE_RESPONSES: Dict[str, Dict[str, str]] = {
    "grief": {
        "en": (
            "I am so deeply sorry for your loss. Losing a baby is one of the most "
            "painful experiences a mother can go through. Your grief is completely "
            "valid, and there is no right or wrong way to feel. Please know that "
            "you are not alone, and support is available whenever you are ready."
        ),
        "sw": (
            "Pole sana kwa msiba wako. Kupoteza mtoto ni moja ya matukio ya "
            "uchungu zaidi ambayo mama anaweza kupitia. Huzuni yako ni halali "
            "kabisa. Tafadhali jua kwamba huko peke yako, na msaada unapatikana."
        ),
    },
    "anxiety": {
        "en": (
            "It is completely understandable to feel anxious during pregnancy. "
            "Your feelings are valid. Let us take this one step at a time. "
            "Would you like to share more about what is worrying you?"
        ),
        "sw": (
            "Ni kawaida kabisa kuhisi wasiwasi wakati wa ujauzito. "
            "Hisia zako ni za kweli. Hebu tushughulikie hili hatua moja kwa wakati mmoja."
        ),
    },
    "depression": {
        "en": (
            "Thank you for trusting me with how you are feeling. What you are "
            "experiencing sounds very difficult, and you deserve support. "
            "You are not a bad mother for feeling this way - these feelings "
            "can be a sign that you need and deserve care too."
        ),
        "sw": (
            "Asante kwa kuniambia hisia zako. Unachopitia kinaonekana kuwa "
            "kigumu sana, na unastahili msaada. Hisia hizi zinaweza kuwa ishara "
            "kwamba wewe pia unahitaji na unastahili huduma."
        ),
    },
    "crisis": {
        "en": (
            "I hear you, and I am very concerned about your safety right now. "
            "You matter deeply, and so does your baby. Please reach out to "
            "emergency services or a crisis line immediately. You do not have "
            "to face this alone."
        ),
        "sw": (
            "Nakusikia, na ninahangaika sana kuhusu usalama wako sasa hivi. "
            "Wewe ni muhimu sana, na mtoto wako pia. Tafadhali wasiliana na "
            "huduma za dharura au mstari wa msaada mara moja."
        ),
    },
    "joy": {
        "en": (
            "It is wonderful to hear you are feeling positive! "
            "Your wellbeing matters so much. Keep nurturing yourself "
            "and your growing baby."
        ),
        "sw": (
            "Ni vizuri kusikia kwamba unajisikia vizuri! "
            "Afya yako ni muhimu sana. Endelea kujitunza wewe na mtoto wako anayekua."
        ),
    },
    "neutral": {
        "en": (
            "Thank you for sharing. How are you feeling today about your pregnancy? "
            "I am here to listen and support you."
        ),
        "sw": (
            "Asante kwa kushiriki. Unajisikiaje leo kuhusu ujauzito wako? "
            "Niko hapa kukusikia na kukusaidia."
        ),
    },
}


# ---------------------------------------------------------------------------
# EmotionDetector
# ---------------------------------------------------------------------------

class EmotionDetector:
    """
    Detects emotional states and mental health risk from maternal text input.

    Combines keyword pattern matching, sentiment analysis, and EPDS scoring
    to provide compassionate, clinically-informed emotional support guidance.
    """

    def __init__(self) -> None:
        self._compiled_patterns = self._compile_patterns()

    def detect(self, inp: EmotionInput) -> EmotionOutput:
        """
        Perform emotion detection and mental health risk assessment.

        Args:
            inp: EmotionInput with text and optional context.

        Returns:
            EmotionOutput with emotion labels, risk scores, and recommendations.
        """
        text_lower = inp.text.lower()
        lang = inp.language if inp.language in ("en", "sw", "fr") else "en"

        # 1. Pattern matching
        crisis_detected, crisis_type = self._detect_crisis(text_lower)
        grief_indicators = self._detect_grief(text_lower, inp.context)
        anxiety_score = self._score_pattern(text_lower, "anxiety")
        depression_score = self._score_pattern(text_lower, "depression")
        joy_score = self._score_pattern(text_lower, "joy")
        anger_score = self._score_pattern(text_lower, "anger")
        loneliness_score = self._score_pattern(text_lower, "loneliness")

        # 2. Audio modifiers
        if inp.audio_features:
            anxiety_score = self._apply_audio_modifiers(
                inp.audio_features, anxiety_score, depression_score
            )

        # 3. EPDS scoring
        epds_score: Optional[int] = None
        epds_risk_level: Optional[str] = None
        if inp.epds_responses:
            try:
                epds_score, epds_risk_level = score_epds(inp.epds_responses)
                # Boost depression score based on EPDS
                if epds_score >= 13:
                    depression_score = max(depression_score, 0.80)
                elif epds_score >= 10:
                    depression_score = max(depression_score, 0.55)
                elif epds_score >= 7:
                    depression_score = max(depression_score, 0.30)
                # Check item 10 (suicidal ideation)
                if inp.epds_responses[9] >= 2:
                    crisis_detected = True
                    crisis_type = "suicidal_ideation_epds"
            except ValueError as e:
                logger.warning("EPDS scoring error: %s", e)

        # 4. Grief context boost
        if inp.context in ("post_miscarriage", "stillbirth", "neonatal_loss"):
            grief_indicators.append("context_loss")
            depression_score = max(depression_score, 0.40)

        # 5. Primary emotion
        primary_emotion = self._determine_primary_emotion(
            crisis_detected, grief_indicators, anxiety_score,
            depression_score, joy_score, anger_score, loneliness_score,
        )

        # 6. Secondary emotions
        secondary_emotions = self._determine_secondary_emotions(
            primary_emotion, anxiety_score, depression_score,
            joy_score, anger_score, loneliness_score, grief_indicators,
        )

        # 7. Distress level
        distress_level = self._calculate_distress(
            crisis_detected, grief_indicators, anxiety_score,
            depression_score, loneliness_score,
        )

        # 8. Requires immediate support
        requires_immediate = crisis_detected or distress_level >= 0.70

        # 9. Response tone
        response_tone = self._determine_response_tone(
            crisis_detected, primary_emotion, distress_level
        )

        # 10. Compassionate response
        compassionate_response = self._build_compassionate_response(
            primary_emotion, crisis_detected, lang
        )

        # 11. Escalation message
        escalation_message = self._build_escalation_message(
            crisis_detected, crisis_type, distress_level, lang
        )

        # 12. Support resources
        support_resources = SUPPORT_RESOURCES.get(lang, SUPPORT_RESOURCES["en"])

        return EmotionOutput(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            distress_level=round(distress_level, 4),
            grief_indicators=grief_indicators,
            depression_risk=round(depression_score, 4),
            epds_score=epds_score,
            epds_risk_level=epds_risk_level,
            requires_immediate_support=requires_immediate,
            recommended_response_tone=response_tone,
            crisis_detected=crisis_detected,
            crisis_type=crisis_type,
            compassionate_response=compassionate_response,
            escalation_message=escalation_message,
            support_resources=support_resources,
        )

    # ------------------------------------------------------------------
    # Detection methods
    # ------------------------------------------------------------------

    def _detect_crisis(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect suicidal ideation or self-harm signals."""
        for pattern in self._compiled_patterns["crisis"]:
            if pattern.search(text):
                return True, "suicidal_ideation"
        return False, None

    def _detect_grief(self, text: str, context: str) -> List[str]:
        """Detect grief indicators from text and context."""
        indicators: List[str] = []
        for pattern in self._compiled_patterns["grief"]:
            if pattern.search(text):
                indicators.append(pattern.pattern[:30])
        if context in ("post_miscarriage", "stillbirth", "neonatal_loss"):
            indicators.append(f"context:{context}")
        return indicators

    def _score_pattern(self, text: str, category: str) -> float:
        """Score text against a pattern category (0-1)."""
        patterns = self._compiled_patterns.get(category, [])
        matches = sum(1 for p in patterns if p.search(text))
        return min(matches / max(len(patterns), 1) * 2.5, 1.0)

    def _apply_audio_modifiers(
        self,
        audio: AudioFeatures,
        anxiety_score: float,
        depression_score: float,
    ) -> float:
        """Modify anxiety score based on audio features."""
        modifier = 0.0
        if audio.tremor_detected:
            modifier += 0.15
        if audio.pitch_variance > 50:
            modifier += 0.10
        if audio.speech_rate < 80:  # slow speech -> possible depression
            depression_score = min(depression_score + 0.10, 1.0)
        if audio.pause_frequency > 5:
            modifier += 0.08
        return min(anxiety_score + modifier, 1.0)

    # ------------------------------------------------------------------
    # Classification helpers
    # ------------------------------------------------------------------

    def _determine_primary_emotion(
        self,
        crisis: bool,
        grief: List[str],
        anxiety: float,
        depression: float,
        joy: float,
        anger: float,
        loneliness: float,
    ) -> PrimaryEmotion:
        if crisis:
            return PrimaryEmotion.HOPELESSNESS
        if grief:
            return PrimaryEmotion.GRIEF
        scores = {
            PrimaryEmotion.ANXIETY: anxiety,
            PrimaryEmotion.SADNESS: depression,
            PrimaryEmotion.JOY: joy,
            PrimaryEmotion.ANGER: anger,
            PrimaryEmotion.LONELINESS: loneliness,
        }
        best = max(scores, key=lambda k: scores[k])
        if scores[best] < 0.10:
            return PrimaryEmotion.NEUTRAL
        return best

    def _determine_secondary_emotions(
        self,
        primary: PrimaryEmotion,
        anxiety: float,
        depression: float,
        joy: float,
        anger: float,
        loneliness: float,
        grief: List[str],
    ) -> List[str]:
        secondary: List[str] = []
        threshold = 0.15
        emotion_map = {
            "anxiety": anxiety,
            "sadness": depression,
            "joy": joy,
            "anger": anger,
            "loneliness": loneliness,
        }
        for name, score in emotion_map.items():
            if score >= threshold and name != primary.value:
                secondary.append(name)
        if grief and primary != PrimaryEmotion.GRIEF:
            secondary.append("grief")
        return secondary[:3]

    def _calculate_distress(
        self,
        crisis: bool,
        grief: List[str],
        anxiety: float,
        depression: float,
        loneliness: float,
    ) -> float:
        if crisis:
            return 1.0
        score = (
            depression * 0.40 +
            anxiety * 0.30 +
            loneliness * 0.15 +
            (0.30 if grief else 0.0)
        )
        return min(score, 1.0)

    def _determine_response_tone(
        self,
        crisis: bool,
        primary: PrimaryEmotion,
        distress: float,
    ) -> ResponseTone:
        if crisis:
            return ResponseTone.CRISIS_IMMEDIATE
        if primary == PrimaryEmotion.GRIEF:
            return ResponseTone.EMPATHETIC_GRIEF
        if distress >= 0.60:
            return ResponseTone.URGENT_CARING
        if primary in (PrimaryEmotion.ANXIETY, PrimaryEmotion.FEAR):
            return ResponseTone.CALM_REASSURING
        if primary == PrimaryEmotion.JOY:
            return ResponseTone.WARM_SUPPORTIVE
        return ResponseTone.WARM_SUPPORTIVE

    # ------------------------------------------------------------------
    # Response builders
    # ------------------------------------------------------------------

    def _build_compassionate_response(
        self,
        primary: PrimaryEmotion,
        crisis: bool,
        lang: str,
    ) -> str:
        if crisis:
            key = "crisis"
        elif primary == PrimaryEmotion.GRIEF:
            key = "grief"
        elif primary in (PrimaryEmotion.ANXIETY, PrimaryEmotion.FEAR):
            key = "anxiety"
        elif primary in (PrimaryEmotion.SADNESS, PrimaryEmotion.HOPELESSNESS):
            key = "depression"
        elif primary == PrimaryEmotion.JOY:
            key = "joy"
        else:
            key = "neutral"

        responses = COMPASSIONATE_RESPONSES.get(key, COMPASSIONATE_RESPONSES["neutral"])
        return responses.get(lang, responses.get("en", ""))

    def _build_escalation_message(
        self,
        crisis: bool,
        crisis_type: Optional[str],
        distress: float,
        lang: str,
    ) -> Optional[str]:
        if crisis:
            if lang == "sw":
                return (
                    "DHARURA: Mtumiaji anaonyesha dalili za hatari. "
                    "Tafadhali wasiliana na mshauri au huduma za dharura mara moja."
                )
            return (
                "ALERT: User is showing signs of crisis. "
                "Please connect them with a counselor or emergency services immediately."
            )
        if distress >= 0.70:
            if lang == "sw":
                return "Mtumiaji anaonyesha msongo mkubwa wa mawazo. Inashauriwa kufuatilia."
            return "User is showing high distress. Follow-up with a mental health professional is recommended."
        return None

    # ------------------------------------------------------------------
    # Pattern compilation
    # ------------------------------------------------------------------

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        return {
            "crisis": [re.compile(p, re.IGNORECASE) for p in CRISIS_PATTERNS],
            "grief": [re.compile(p, re.IGNORECASE) for p in GRIEF_PATTERNS],
            "anxiety": [re.compile(p, re.IGNORECASE) for p in ANXIETY_PATTERNS],
            "depression": [re.compile(p, re.IGNORECASE) for p in DEPRESSION_PATTERNS],
            "joy": [re.compile(p, re.IGNORECASE) for p in JOY_PATTERNS],
            "anger": [re.compile(p, re.IGNORECASE) for p in ANGER_PATTERNS],
            "loneliness": [re.compile(p, re.IGNORECASE) for p in LONELINESS_PATTERNS],
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def detect_emotion(
    text: str,
    context: str = "",
    language: str = "en",
    epds_responses: Optional[List[int]] = None,
) -> EmotionOutput:
    """
    Quick emotion detection wrapper.

    Example:
        result = detect_emotion(
            "I feel so alone and scared about my pregnancy",
            context="third_trimester",
            language="en",
        )
    """
    inp = EmotionInput(
        text=text,
        context=context,
        language=language,
        epds_responses=epds_responses,
    )
    detector = EmotionDetector()
    return detector.detect(inp)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json as _json

    test_cases = [
        {
            "text": "I lost my baby last week. I feel so empty and broken.",
            "context": "post_miscarriage",
            "language": "en",
        },
        {
            "text": "I am so worried about my baby. What if something is wrong?",
            "context": "third_trimester",
            "language": "en",
        },
        {
            "text": "I feel like I want to hurt myself. I cannot do this anymore.",
            "context": "",
            "language": "en",
        },
        {
            "text": "Nimefurahi sana! Mtoto wangu anakua vizuri.",
            "context": "second_trimester",
            "language": "sw",
        },
    ]

    detector = EmotionDetector()
    for case in test_cases:
        inp = EmotionInput(**case)
        result = detector.detect(inp)
        print(f"\nText: {case['text'][:60]}...")
        print(f"  Primary emotion:  {result.primary_emotion.value}")
        print(f"  Distress level:   {result.distress_level:.2f}")
        print(f"  Depression risk:  {result.depression_risk:.2f}")
        print(f"  Crisis detected:  {result.crisis_detected}")
        print(f"  Response tone:    {result.recommended_response_tone.value}")
        if result.crisis_detected:
            print(f"  ESCALATION: {result.escalation_message}")
