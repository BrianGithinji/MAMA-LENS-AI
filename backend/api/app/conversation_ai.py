"""
MAMA-LENS AI - Multilingual Conversational AI for Maternal Health
Supports English, Swahili, French, Arabic with GPT-4o integration,
intent classification, emergency escalation, and culturally aware responses.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Intent(str, Enum):
    SYMPTOM_CHECK = "symptom_check"
    APPOINTMENT_BOOKING = "appointment_booking"
    EDUCATION_REQUEST = "education_request"
    EMOTIONAL_SUPPORT = "emotional_support"
    EMERGENCY = "emergency"
    MEDICATION_QUERY = "medication_query"
    NUTRITION_ADVICE = "nutrition_advice"
    EXERCISE_ADVICE = "exercise_advice"
    FETAL_MOVEMENT = "fetal_movement"
    LABOR_SIGNS = "labor_signs"
    POSTPARTUM = "postpartum"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class MessageChannel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    USSD = "ussd"
    APP = "app"
    WEB = "web"


class LiteracyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ConversationMessage:
    role: str          # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    intent: Optional[str] = None


@dataclass
class ConversationContext:
    """Maintains state across a conversation session."""
    session_id: str
    language: str = "en"
    literacy_level: LiteracyLevel = LiteracyLevel.MEDIUM
    channel: MessageChannel = MessageChannel.APP
    gestational_age_weeks: Optional[int] = None
    user_name: Optional[str] = None
    messages: List[ConversationMessage] = field(default_factory=list)
    current_intent: Optional[Intent] = None
    risk_level: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_message(self, role: str, content: str, intent: Optional[str] = None) -> None:
        self.messages.append(ConversationMessage(role=role, content=content, intent=intent))
        self.last_updated = datetime.utcnow().isoformat()

    def get_recent_messages(self, n: int = 10) -> List[Dict[str, str]]:
        """Return last n messages in OpenAI format."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages[-n:]
        ]


@dataclass
class ConversationResponse:
    """Response from the conversational AI."""
    message: str
    intent: Intent
    is_emergency: bool
    emergency_type: Optional[str]
    suggested_actions: List[str]
    education_content: Optional[str]
    follow_up_questions: List[str]
    requires_human_handoff: bool
    confidence: float
    language: str


# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

INTENT_PATTERNS: Dict[str, List[str]] = {
    Intent.EMERGENCY: [
        # English
        r"\b(bleeding|hemorrhage|seizure|unconscious|not\s+breathing|cord\s+prolapse)\b",
        r"\b(severe\s+pain|chest\s+pain|can.t\s+breathe|baby\s+not\s+moving)\b",
        r"\b(emergency|urgent|help\s+me|dying|ambulance|hospital\s+now)\b",
        r"\b(heavy\s+bleeding|blood\s+clots|water\s+broke|preterm\s+labor)\b",
        # Kiswahili
        r"\b(damu\s+nyingi|kutoka\s+damu|degedege|mshtuko|kupoteza\s+fahamu)\b",
        r"\b(mtoto\s+hasogei|dharura|maumivu\s+makali|ugumu\s+wa\s+kupumua)\b",
        r"\b(maji\s+yamevunjika|kuzaa\s+mapema|msaada\s+wa\s+haraka)\b",
    ],
    Intent.SYMPTOM_CHECK: [
        # English
        r"\b(feeling|symptom|pain|ache|nausea|vomiting|swelling|headache)\b",
        r"\b(dizzy|faint|tired|fatigue|cramp|discharge|spotting|fever)\b",
        r"\b(is\s+it\s+normal|should\s+i\s+worry|what\s+does\s+it\s+mean)\b",
        # Kiswahili
        r"\b(ninajisikia|dalili|maumivu|kichefuchefu|kutapika|uvimbe|homa)\b",
        r"\b(kizunguzungu|uchovu|tumbo\s+kuuma|kutokwa|madoa|ni\s+kawaida)\b",
        r"\b(ninaumwa|kuna\s+tatizo|sijisikii\s+vizuri|mwili\s+wangu)\b",
    ],
    Intent.APPOINTMENT_BOOKING: [
        # English
        r"\b(appointment|book|schedule|visit|clinic|anc|checkup|doctor)\b",
        r"\b(when\s+should\s+i|next\s+visit|how\s+often|prenatal\s+care)\b",
        # Kiswahili
        r"\b(miadi|kliniki|ziara|daktari|mkunga|kliniki\s+ya\s+uzazi|ANC)\b",
        r"\b(niende\s+lini|ziara\s+ya\s+kliniki|huduma\s+ya\s+uzazi|kupanga)\b",
        r"\b(hospitali|kituo\s+cha\s+afya|kutembelea\s+daktari)\b",
    ],
    Intent.NUTRITION_ADVICE: [
        # English
        r"\b(eat|food|diet|nutrition|vitamin|iron|folic|supplement|meal)\b",
        r"\b(what\s+to\s+eat|healthy\s+food|avoid\s+eating|safe\s+to\s+eat)\b",
        # Kiswahili
        r"\b(kula|chakula|lishe|vitamini|chuma|asidi\s+ya\s+foliki|virutubisho)\b",
        r"\b(nile\s+nini|chakula\s+bora|epuka\s+kula|salama\s+kula|mlo)\b",
        r"\b(mboga|matunda|protini|kalsiamu|madini|maziwa|mayai|samaki)\b",
        r"\b(njaa|kula\s+vizuri|lishe\s+bora|chakula\s+cha\s+ujauzito)\b",
    ],
    Intent.EMOTIONAL_SUPPORT: [
        # English
        r"\b(sad|anxious|scared|worried|depressed|lonely|overwhelmed|stressed)\b",
        r"\b(feel\s+like|can.t\s+cope|too\s+much|breaking\s+down|crying)\b",
        r"\b(support|talk|listen|help\s+me\s+feel|not\s+okay)\b",
        # Kiswahili
        r"\b(huzuni|wasiwasi|hofu|msongo|upweke|nimechoka|ninalia)\b",
        r"\b(sijisikii\s+vizuri|siwezi\s+kukabiliana|msaada|zungumza\s+nami)\b",
        r"\b(nimepoteza\s+mtoto|kuharibika\s+kwa\s+mimba|huzuni\s+yangu)\b",
        r"\b(ninajisikia\s+peke\s+yangu|hakuna\s+anayenielewa|nimechoshwa)\b",
    ],
    Intent.EDUCATION_REQUEST: [
        # English
        r"\b(tell\s+me|explain|what\s+is|how\s+does|learn|information|about)\b",
        r"\b(week\s+\d+|trimester|development|baby\s+size|fetal\s+growth)\b",
        # Kiswahili
        r"\b(niambie|eleza|ni\s+nini|jinsi\s+gani|habari|maelezo|kuhusu)\b",
        r"\b(wiki\s+ya\s+\d+|trimesta|ukuaji\s+wa\s+mtoto|ukubwa\s+wa\s+mtoto)\b",
        r"\b(nataka\s+kujua|nifundishe|maswali\s+kuhusu\s+ujauzito)\b",
    ],
    Intent.MEDICATION_QUERY: [
        # English
        r"\b(medicine|medication|drug|tablet|pill|safe\s+to\s+take|prescription)\b",
        r"\b(paracetamol|iron\s+tablet|folic\s+acid|antibiotic|dose)\b",
        # Kiswahili
        r"\b(dawa|tembe|kidonge|salama\s+kutumia|dawa\s+ya\s+daktari)\b",
        r"\b(paracetamol|tembe\s+za\s+chuma|asidi\s+ya\s+foliki|antibiotiki|kipimo)\b",
        r"\b(ninaweza\s+kutumia|dawa\s+gani|dawa\s+za\s+ujauzito)\b",
    ],
    Intent.FETAL_MOVEMENT: [
        # English
        r"\b(baby\s+moving|kick|movement|fetal\s+movement|not\s+kicking)\b",
        r"\b(kick\s+count|baby\s+active|baby\s+quiet|no\s+movement)\b",
        # Kiswahili
        r"\b(mtoto\s+anasogea|mateke|mwendo\s+wa\s+mtoto|mtoto\s+hasogei)\b",
        r"\b(kuhesabu\s+mateke|mtoto\s+ana\s+nguvu|mtoto\s+kimya|hakuna\s+mwendo)\b",
        r"\b(mtoto\s+wangu\s+anacheza|mtoto\s+amekimya\s+sana)\b",
    ],
    Intent.LABOR_SIGNS: [
        # English
        r"\b(labor|labour|contraction|water\s+broke|mucus\s+plug|dilation)\b",
        r"\b(am\s+i\s+in\s+labor|going\s+into\s+labor|birth|delivery)\b",
        # Kiswahili
        r"\b(mikazo|kujifungua|maji\s+yamevunjika|uchungu|kuzaa)\b",
        r"\b(ninajifungua|dalili\s+za\s+kujifungua|wakati\s+wa\s+kuzaa)\b",
        r"\b(tumbo\s+linakaza|maumivu\s+ya\s+kuzaa|hospitali\s+sasa)\b",
    ],
    Intent.GREETING: [
        # English + Kiswahili
        r"^(hi|hello|hey|good\s+(morning|afternoon|evening))\b",
        r"^(habari|mambo|hujambo|shikamoo|salama|karibu|salam)\b",
        r"\b(habari\s+yako|habari\s+za\s+asubuhi|habari\s+za\s+jioni)\b",
        r"\b(how\s+are\s+you|nice\s+to\s+meet|start|begin|nianze)\b",
    ],
}

# ---------------------------------------------------------------------------
# Emergency keywords (multilingual)
# ---------------------------------------------------------------------------

EMERGENCY_KEYWORDS = {
    "en": ["bleeding", "seizure", "unconscious", "not breathing", "cord prolapse",
           "severe pain", "baby not moving", "heavy bleeding", "emergency"],
    "sw": [
        # Bleeding
        "kutoka damu", "damu nyingi", "damu ukeni", "kutokwa na damu",
        # Seizure
        "degedege", "mshtuko", "kupoteza fahamu", "kuzimia",
        # Pain
        "maumivu makali", "maumivu ya tumbo", "maumivu ya kichwa makali",
        # Fetal
        "mtoto hasogei", "mtoto haonekani kusogea", "hakuna mwendo wa mtoto",
        # Emergency
        "dharura", "msaada wa haraka", "nenda hospitali", "piga simu 999",
        # Breathing
        "ugumu wa kupumua", "kupumua kwa shida",
        # Vision
        "maono mabaya", "kuona vibaya ghafla",
        # Water breaking
        "maji yamevunjika", "mfuko umevunjika",
        # Preterm
        "kuzaa mapema", "mikazo kabla ya wakati",
    ],
    "fr": ["saignement", "convulsion", "inconscient", "douleur severe",
           "bebe ne bouge pas", "urgence", "hemorragie"],
    "ar": ["نزيف", "تشنج", "فقدان الوعي", "ألم شديد", "الطفل لا يتحرك", "طوارئ"],
}

# ---------------------------------------------------------------------------
# Week-by-week education content
# ---------------------------------------------------------------------------

WEEKLY_EDUCATION: Dict[int, Dict[str, str]] = {
    4: {
        "en": "Week 4: Your baby is the size of a poppy seed. The neural tube is forming. Start folic acid if you haven't already.",
        "sw": "Wiki ya 4: Mtoto wako ana ukubwa wa mbegu ndogo. Anza kuchukua asidi ya foliki.",
    },
    8: {
        "en": "Week 8: Your baby is the size of a raspberry. All major organs are forming. Morning sickness is common - eat small frequent meals.",
        "sw": "Wiki ya 8: Mtoto wako ana ukubwa wa tunda la raspberry. Viungo vyote vikuu vinaundwa.",
    },
    12: {
        "en": "Week 12: End of first trimester! Your baby is the size of a lime. Risk of miscarriage decreases significantly. Book your first ANC visit if not done.",
        "sw": "Wiki ya 12: Mwisho wa trimesta ya kwanza! Hatari ya kuharibika kwa mimba inapungua sana.",
    },
    16: {
        "en": "Week 16: Your baby is the size of an avocado. You may start feeling movements soon. Your bump is becoming visible.",
        "sw": "Wiki ya 16: Mtoto wako ana ukubwa wa parachichi. Unaweza kuanza kuhisi mwendo hivi karibuni.",
    },
    20: {
        "en": "Week 20: Halfway there! Your baby is the size of a banana. This is a great time for your anatomy scan ultrasound.",
        "sw": "Wiki ya 20: Nusu ya safari! Mtoto wako ana ukubwa wa ndizi. Wakati mzuri wa ultrasound.",
    },
    24: {
        "en": "Week 24: Your baby is the size of an ear of corn. Baby can now hear your voice. Talk and sing to your baby!",
        "sw": "Wiki ya 24: Mtoto wako ana ukubwa wa mahindi. Mtoto anaweza kusikia sauti yako sasa.",
    },
    28: {
        "en": "Week 28: Third trimester begins! Your baby is the size of an eggplant. Start counting fetal movements daily.",
        "sw": "Wiki ya 28: Trimesta ya tatu inaanza! Anza kuhesabu mwendo wa mtoto kila siku.",
    },
    32: {
        "en": "Week 32: Your baby is the size of a squash. Baby is gaining weight rapidly. Attend your ANC visit and discuss birth plan.",
        "sw": "Wiki ya 32: Mtoto wako ana ukubwa wa boga. Mtoto anapata uzito haraka. Hudhuria kliniki.",
    },
    36: {
        "en": "Week 36: Your baby is the size of a honeydew melon. Baby may drop lower in your pelvis. Watch for labor signs.",
        "sw": "Wiki ya 36: Mtoto wako ana ukubwa wa tikiti. Angalia dalili za kujifungua.",
    },
    40: {
        "en": "Week 40: Full term! Your baby is ready to meet you. Watch for regular contractions, water breaking, or bloody show.",
        "sw": "Wiki ya 40: Mimba imekamilika! Mtoto wako yuko tayari kukutana nawe. Angalia mikazo ya kawaida.",
    },
}

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPTS: Dict[str, str] = {
    "en": """You are MAMA, a compassionate AI maternal health assistant for the MAMA-LENS platform,
serving pregnant women and new mothers primarily in Africa.

Your core principles:
- Be warm, non-judgmental, and culturally sensitive
- Use simple, clear language appropriate to the user's literacy level
- Never replace professional medical advice - always encourage ANC visits
- Detect emergencies immediately and escalate with urgency
- Respect local customs, traditional practices (unless harmful), and family dynamics
- Be aware of resource constraints (limited healthcare access, cost barriers)
- Celebrate milestones and provide emotional encouragement

When responding:
- Keep responses concise for SMS/USSD (under 160 characters if channel is SMS)
- Use bullet points for lists when appropriate
- Always end with an encouraging note or follow-up question
- If unsure, say so and recommend seeing a healthcare provider

Emergency protocol: If you detect ANY emergency symptoms, immediately say:
"URGENT: Please go to the nearest health facility NOW or call emergency services."

You are not a doctor. You provide information and support, not diagnosis.""",

    "sw": """Wewe ni MAMA, msaidizi wa AI wa afya ya uzazi kwa jukwaa la MAMA-LENS.
Unahudumia wanawake wajawazito na mama wapya Afrika Mashariki, hasa Kenya, Tanzania na Uganda.

LUGHA: Jibu DAIMA kwa Kiswahili safi na rahisi. Tumia maneno ya kawaida ya Kiswahili.
Epuka maneno magumu ya kimatibabu — eleza kwa lugha ya kila siku.

Kanuni zako za msingi:
- Kuwa na upole, huruma, na kuzingatia utamaduni wa Afrika Mashariki
- Tumia lugha rahisi inayofaa kiwango cha elimu cha mtumiaji
- Usibadilishe ushauri wa daktari — daima himiza ziara za kliniki ya uzazi (ANC)
- Gundua dharura mara moja na toa msaada wa haraka
- Heshimu desturi za kienyeji na mienendo ya familia
- Zingatia vikwazo vya rasilimali (upatikanaji mdogo wa huduma za afya, gharama)
- Sherehekea hatua muhimu za ujauzito na toa moyo

Msamiati muhimu wa Kiswahili wa afya ya uzazi:
- Ujauzito = pregnancy
- Kujifungua = giving birth / delivery
- Kliniki ya uzazi / ANC = antenatal care clinic
- Mkunga = midwife
- Daktari wa uzazi = obstetrician/gynecologist
- Mtoto tumboni = unborn baby / fetus
- Maumivu ya kujifungua = labour pains / contractions
- Damu nyingi = heavy bleeding
- Degedege = seizure / convulsions
- Shinikizo la damu = blood pressure
- Sukari ya damu = blood sugar / glucose
- Upungufu wa damu = anemia
- Asidi ya foliki = folic acid
- Chuma / madini ya chuma = iron
- Vitamini = vitamins
- Chanjo = vaccination
- Ultrasound / ekografia = ultrasound scan
- Wiki za ujauzito = weeks of pregnancy
- Trimesta = trimester
- Kichefuchefu = nausea / morning sickness
- Uvimbe = swelling / edema
- Maumivu ya kichwa = headache
- Maono mabaya = vision changes / blurred vision
- Mwendo wa mtoto = fetal movement / baby kicks
- Kuhesabu mateke = kick counting
- Kuzaa mapema = preterm birth
- Preeclampsia = preeclampsia (shinikizo la damu + protini kwenye mkojo)
- Kisukari cha ujauzito = gestational diabetes
- Kuharibika kwa mimba = miscarriage
- Huzuni baada ya kupoteza mtoto = grief after pregnancy loss

Wakati wa kujibu:
- Jibu kwa Kiswahili DAIMA isipokuwa mtumiaji aandike kwa lugha nyingine
- Weka majibu mafupi kwa SMS/USSD (chini ya herufi 160)
- Tumia orodha kwa hatua na maelekezo
- Maliza na neno la kutia moyo au swali la ufuatiliaji
- Kama hujui, sema hivyo na pendekeza kuona daktari au mkunga

Itifaki ya dharura: Ukigundua dalili YOYOTE ya dharura, sema mara moja:
"DHARURA: Tafadhali nenda kituo cha afya kilicho karibu SASA HIVI au piga simu 999/112."

Wewe si daktari. Unatoa taarifa na msaada, si utambuzi wa magonjwa.""",
}


# ---------------------------------------------------------------------------
# ConversationalAI
# ---------------------------------------------------------------------------

class ConversationalAI:
    """
    Multilingual conversational AI for maternal health support.

    Integrates Mistral AI for natural language responses with rule-based
    intent classification, emergency detection, and education delivery.
    """

    def __init__(self, mistral_api_key: Optional[str] = None) -> None:
        self.api_key = mistral_api_key or os.getenv("MISTRAL_API_KEY", "")
        self._intent_patterns = self._compile_intent_patterns()
        self._emergency_patterns = self._compile_emergency_patterns()
        self._sessions: Dict[str, ConversationContext] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(
        self,
        session_id: str,
        user_message: str,
        language: str = "en",
        channel: str = "app",
        literacy_level: str = "medium",
        gestational_age_weeks: Optional[int] = None,
    ) -> ConversationResponse:
        """
        Process a user message and return a conversational response.

        Args:
            session_id: Unique session identifier.
            user_message: The user's message text.
            language: Language code (en/sw/fr/ar).
            channel: Message channel (app/whatsapp/sms/ussd).
            literacy_level: User literacy level (low/medium/high).
            gestational_age_weeks: Current gestational age if known.

        Returns:
            ConversationResponse with message and metadata.
        """
        # Get or create session
        ctx = self._get_or_create_session(
            session_id, language, channel, literacy_level, gestational_age_weeks
        )

        # Add user message to history
        ctx.add_message("user", user_message)

        # 1. Emergency check (highest priority)
        is_emergency, emergency_type = self._check_emergency(user_message, language)

        # 2. Intent classification
        intent = self._classify_intent(user_message)

        if is_emergency:
            intent = Intent.EMERGENCY

        ctx.current_intent = intent

        # 3. Education content for relevant intents
        education_content = self._get_education_content(
            intent, gestational_age_weeks or ctx.gestational_age_weeks, language
        )

        # 4. Generate response
        if is_emergency:
            response_text = self._emergency_response(emergency_type, language)
            requires_handoff = True
            confidence = 1.0
        else:
            response_text, confidence = self._generate_response(
                ctx, user_message, intent, language, literacy_level, channel
            )
            requires_handoff = intent == Intent.EMOTIONAL_SUPPORT and confidence < 0.6

        # 5. Simplify for low literacy / SMS
        if literacy_level == "low" or channel in ("sms", "ussd"):
            response_text = self._simplify_response(response_text, channel)

        # 6. Suggested actions
        suggested_actions = self._get_suggested_actions(intent, language)

        # 7. Follow-up questions
        follow_up = self._get_follow_up_questions(intent, language)

        # Add assistant response to history
        ctx.add_message("assistant", response_text, intent=intent.value)

        return ConversationResponse(
            message=response_text,
            intent=intent,
            is_emergency=is_emergency,
            emergency_type=emergency_type,
            suggested_actions=suggested_actions,
            education_content=education_content,
            follow_up_questions=follow_up,
            requires_human_handoff=requires_handoff,
            confidence=confidence,
            language=language,
        )

    def get_weekly_education(
        self, gestational_age_weeks: int, language: str = "en"
    ) -> str:
        """Return week-specific pregnancy education content."""
        # Find closest week
        available_weeks = sorted(WEEKLY_EDUCATION.keys())
        closest = min(available_weeks, key=lambda w: abs(w - gestational_age_weeks))
        content = WEEKLY_EDUCATION.get(closest, {})
        return content.get(language, content.get("en", ""))

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve an existing session."""
        return self._sessions.get(session_id)

    def clear_session(self, session_id: str) -> None:
        """Clear a conversation session."""
        self._sessions.pop(session_id, None)

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def _get_or_create_session(
        self,
        session_id: str,
        language: str,
        channel: str,
        literacy_level: str,
        gestational_age_weeks: Optional[int],
    ) -> ConversationContext:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationContext(
                session_id=session_id,
                language=language,
                literacy_level=LiteracyLevel(literacy_level),
                channel=MessageChannel(channel) if channel in [c.value for c in MessageChannel] else MessageChannel.APP,
                gestational_age_weeks=gestational_age_weeks,
            )
        else:
            ctx = self._sessions[session_id]
            if gestational_age_weeks:
                ctx.gestational_age_weeks = gestational_age_weeks
        return self._sessions[session_id]

    # ------------------------------------------------------------------
    # Intent classification
    # ------------------------------------------------------------------

    def _classify_intent(self, text: str) -> Intent:
        """Classify user intent using pattern matching."""
        text_lower = text.lower()
        scores: Dict[Intent, int] = {}

        for intent_str, patterns in self._intent_patterns.items():
            intent = Intent(intent_str)
            score = sum(1 for p in patterns if p.search(text_lower))
            if score > 0:
                scores[intent] = score

        if not scores:
            return Intent.GENERAL_QUESTION

        return max(scores, key=lambda k: scores[k])

    # ------------------------------------------------------------------
    # Emergency detection
    # ------------------------------------------------------------------

    def _check_emergency(
        self, text: str, language: str
    ) -> Tuple[bool, Optional[str]]:
        """Check for emergency keywords in any supported language."""
        text_lower = text.lower()

        # Check compiled patterns
        for pattern in self._emergency_patterns:
            if pattern.search(text_lower):
                return True, "obstetric_emergency"

        # Check multilingual keywords
        for lang, keywords in EMERGENCY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    return True, "obstetric_emergency"

        return False, None

    def _emergency_response(
        self, emergency_type: Optional[str], language: str
    ) -> str:
        responses = {
            "en": (
                "🚨 URGENT: This sounds like a medical emergency. "
                "Please go to the nearest health facility IMMEDIATELY "
                "or call emergency services (999 / 112). Do not wait. "
                "If you cannot travel, call someone to help you now."
            ),
            "sw": (
                "🚨 DHARURA: Hii inaonekana kama dharura ya kimatibabu.\n\n"
                "Tafadhali FANYA HIVI SASA:\n"
                "1. Nenda kituo cha afya kilicho karibu MARA MOJA\n"
                "2. Au piga simu: 999 au 112\n"
                "3. Mwambie mtu wa karibu nawe akusaidie\n\n"
                "USISUBIRI. Maisha yako na ya mtoto wako ni muhimu sana."
            ),
            "fr": (
                "🚨 URGENT: Cela ressemble a une urgence medicale. "
                "Veuillez vous rendre IMMEDIATEMENT a l etablissement de sante "
                "le plus proche ou appeler les services d urgence (999/112)."
            ),
            "ar": (
                "🚨 عاجل: يبدو هذا حالة طوارئ طبية. "
                "يرجى التوجه فورا إلى أقرب مرفق صحي "
                "أو الاتصال بخدمات الطوارئ 999/112."
            ),
        }
        return responses.get(language, responses["en"])

    # ------------------------------------------------------------------
    # Response generation
    # ------------------------------------------------------------------

    def _generate_response(
        self,
        ctx: ConversationContext,
        user_message: str,
        intent: Intent,
        language: str,
        literacy_level: str,
        channel: str,
    ) -> Tuple[str, float]:
        """Generate response using Mistral AI or fallback to rule-based."""
        if self.api_key:
            try:
                return self._mistral_response(ctx, user_message, intent, language, literacy_level, channel)
            except Exception as exc:
                logger.warning("Mistral AI call failed: %s. Using fallback.", exc)

        return self._rule_based_response(intent, language, literacy_level), 0.70

    def _mistral_response(
        self,
        ctx: ConversationContext,
        user_message: str,
        intent: Intent,
        language: str,
        literacy_level: str,
        channel: str,
    ) -> Tuple[str, float]:
        """Call Mistral AI API for response generation."""
        try:
            from mistralai.client.sdk import Mistral  # type: ignore

            client = Mistral(api_key=self.api_key)

            system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

            context_additions = []
            if ctx.gestational_age_weeks:
                context_additions.append(
                    f"The user is {ctx.gestational_age_weeks} weeks pregnant."
                )
            if literacy_level == "low":
                context_additions.append(
                    "Use very simple language. Short sentences. Avoid medical jargon."
                )
            if channel in ("sms", "ussd"):
                context_additions.append(
                    "Keep your response under 160 characters for SMS compatibility."
                )
            if ctx.risk_level in ("high", "emergency"):
                context_additions.append(
                    f"This user has been assessed as {ctx.risk_level} risk. Be extra attentive."
                )

            if context_additions:
                system_prompt += "\n\nContext: " + " ".join(context_additions)

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(ctx.get_recent_messages(8))

            response = client.chat.complete(
                model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
                messages=messages,
                max_tokens=500 if channel not in ("sms", "ussd") else 100,
                temperature=0.7,
            )

            text = response.choices[0].message.content or ""
            return text.strip(), 0.92

        except ImportError:
            logger.warning("mistralai package not installed.")
            raise
        except Exception as exc:
            logger.error("Mistral AI error: %s", exc)
            raise

    def _rule_based_response(
        self, intent: Intent, language: str, literacy_level: str
    ) -> str:
        """Fallback rule-based responses by intent — full Kiswahili support."""
        responses: Dict[Intent, Dict[str, str]] = {
            Intent.GREETING: {
                "en": "Hello! I am MAMA, your maternal health assistant. How are you feeling today? How can I help you?",
                "sw": (
                    "Habari! Mimi ni MAMA, msaidizi wako wa afya ya uzazi. 💚\n"
                    "Unajisikiaje leo? Ninaweza kukusaidia vipi?\n\n"
                    "Unaweza kuniuliza kuhusu:\n"
                    "• Dalili za ujauzito\n"
                    "• Lishe na chakula\n"
                    "• Ziara za kliniki (ANC)\n"
                    "• Mwendo wa mtoto\n"
                    "• Msaada wa kihisia\n\n"
                    "Niko hapa kukusaidia!"
                ),
                "fr": "Bonjour! Je suis MAMA, votre assistante de sante maternelle. Comment vous sentez-vous aujourd hui?",
            },
            Intent.SYMPTOM_CHECK: {
                "en": "I hear you are experiencing some symptoms. Can you describe them in more detail? When did they start? Are they getting worse?",
                "sw": (
                    "Nakusikia una dalili fulani. Niambie zaidi:\n\n"
                    "• Dalili zinaanza lini?\n"
                    "• Zinazidi kuwa mbaya?\n"
                    "• Uko wiki ngapi za ujauzito?\n\n"
                    "⚠️ Nenda hospitali MARA MOJA ukiwa na:\n"
                    "• Damu nyingi ukeni\n"
                    "• Maumivu makali ya kichwa\n"
                    "• Mtoto hasogei (baada ya wiki 28)\n"
                    "• Degedege au kuzimia\n\n"
                    "Elezea dalili zako na nitakusaidia."
                ),
                "fr": "Je vous entends avoir des symptomes. Pouvez-vous les decrire plus en detail?",
            },
            Intent.NUTRITION_ADVICE: {
                "en": "Good nutrition is vital during pregnancy. Focus on: iron-rich foods (beans, dark leafy greens, meat), folic acid (green vegetables), protein (eggs, fish, legumes), and calcium (milk, yogurt). Drink plenty of clean water.",
                "sw": (
                    "Lishe bora ni muhimu sana wakati wa ujauzito! 🥗\n\n"
                    "✅ Kula kila siku:\n"
                    "• Chuma: maharagwe, mboga za majani (sukuma wiki, spinachi), nyama, dagaa\n"
                    "• Asidi ya foliki: mboga za kijani, mayai, karanga\n"
                    "• Protini: mayai, samaki, kuku, maharagwe, dengu\n"
                    "• Kalsiamu: maziwa, mtindi, mboga za majani\n"
                    "• Maji: glasi 8-10 kila siku\n\n"
                    "❌ Epuka:\n"
                    "• Pombe (kabisa)\n"
                    "• Nyama mbichi au isiyopikwa vizuri\n"
                    "• Chai/kahawa nyingi sana\n"
                    "• Vyakula visivyo na usafi\n\n"
                    "💊 Chukua tembe za chuma na asidi ya foliki kila siku kama ilivyoagizwa na daktari."
                ),
            },
            Intent.APPOINTMENT_BOOKING: {
                "en": "Regular ANC visits are very important. WHO recommends at least 8 visits during pregnancy. Your next visit should be scheduled based on your current week. Would you like help finding a nearby clinic?",
                "sw": (
                    "Ziara za kliniki ya uzazi (ANC) ni muhimu sana! 🏥\n\n"
                    "WHO inapendekeza angalau ziara 8:\n"
                    "• Wiki 12 — ziara ya kwanza\n"
                    "• Wiki 20 — ultrasound ya anatomy\n"
                    "• Wiki 26, 30, 34, 36, 38, 40\n\n"
                    "📋 Kila ziara: pima shinikizo la damu, uzito, na afya ya mtoto.\n\n"
                    "Lete kadi yako ya ANC kila ziara.\n"
                    "Je, unahitaji msaada kupata kliniki karibu nawe?"
                ),
            },
            Intent.EMOTIONAL_SUPPORT: {
                "en": "I hear you, and your feelings are completely valid. Pregnancy can be an emotional journey. You are not alone. Would you like to talk more about how you are feeling?",
                "sw": (
                    "Nakusikia, na hisia zako ni za kweli kabisa. 💚\n\n"
                    "Ujauzito unaweza kuleta hisia nyingi — furaha, wasiwasi, hofu, na huzuni. "
                    "Hizi zote ni za kawaida.\n\n"
                    "Huko peke yako. Niko hapa kukusikia.\n\n"
                    "Ungependa kuzungumza zaidi kuhusu unavyohisi?\n\n"
                    "Kama unahisi huzuni kali au wasiwasi mkubwa, "
                    "tafadhali zungumza na mkunga wako au daktari. "
                    "Unastahili msaada. 🌸"
                ),
            },
            Intent.FETAL_MOVEMENT: {
                "en": "Fetal movements are important to monitor. After 28 weeks, you should feel at least 10 movements in 2 hours. If you notice reduced movement, contact your healthcare provider immediately.",
                "sw": (
                    "Mwendo wa mtoto ni muhimu sana kufuatilia! 👶\n\n"
                    "Baada ya wiki 28:\n"
                    "• Unapaswa kuhisi angalau mateke 10 kwa masaa 2\n"
                    "• Fanya hivi baada ya kula (mtoto huwa na nguvu zaidi)\n"
                    "• Lala upande wa kushoto na uhesabu mateke\n\n"
                    "⚠️ Nenda hospitali MARA MOJA kama:\n"
                    "• Hakuna mwendo kwa masaa 2+\n"
                    "• Mwendo umepungua sana kuliko kawaida\n\n"
                    "Hii inaweza kuwa ishara ya mtoto kuhitaji msaada."
                ),
            },
            Intent.LABOR_SIGNS: {
                "en": "Signs of labor include: regular contractions (every 5 minutes), water breaking, bloody show, and strong back pain. If you are before 37 weeks, go to hospital immediately as this may be preterm labor.",
                "sw": (
                    "Dalili za kujifungua ni:\n\n"
                    "✅ Dalili za kawaida:\n"
                    "• Mikazo ya kawaida (kila dakika 5, kwa saa 1+)\n"
                    "• Maji kuvunjika (mfuko wa mtoto)\n"
                    "• Damu kidogo na kamasi ukeni\n"
                    "• Maumivu ya mgongo wa chini\n\n"
                    "🚨 Nenda hospitali MARA MOJA kama:\n"
                    "• Uko chini ya wiki 37 (kuzaa mapema)\n"
                    "• Damu nyingi\n"
                    "• Mtoto hasogei\n"
                    "• Maumivu makali sana\n\n"
                    "Je, uko wiki ngapi za ujauzito sasa hivi?"
                ),
            },
            Intent.MEDICATION_QUERY: {
                "en": "Always consult your healthcare provider before taking any medication during pregnancy. Iron and folic acid supplements are generally safe and recommended. Avoid NSAIDs like ibuprofen unless prescribed.",
                "sw": (
                    "Kuhusu dawa wakati wa ujauzito:\n\n"
                    "✅ Salama (kama ilivyoagizwa):\n"
                    "• Tembe za chuma (iron) — kila siku\n"
                    "• Asidi ya foliki — hasa miezi 3 ya kwanza\n"
                    "• Paracetamol — kwa maumivu madogo\n"
                    "• Dawa za malaria (IPTp-SP) — kutoka wiki 16\n\n"
                    "❌ Epuka bila ushauri wa daktari:\n"
                    "• Ibuprofen, aspirin (NSAIDs)\n"
                    "• Dawa za mitishamba zisizojulikana\n"
                    "• Dawa yoyote bila agizo la daktari\n\n"
                    "⚠️ DAIMA wasiliana na daktari au mkunga wako kabla ya kutumia dawa yoyote."
                ),
            },
            Intent.GENERAL_QUESTION: {
                "en": "Thank you for your question. I am here to help with your maternal health journey. Could you tell me more about what you would like to know?",
                "sw": (
                    "Asante kwa swali lako. 💚\n"
                    "Niko hapa kukusaidia katika safari yako ya ujauzito.\n\n"
                    "Unaweza kuniuliza kuhusu:\n"
                    "• Dalili na afya yako\n"
                    "• Lishe na chakula\n"
                    "• Ziara za kliniki\n"
                    "• Ukuaji wa mtoto\n"
                    "• Msaada wa kihisia\n\n"
                    "Niambie zaidi — ninakusaidia!"
                ),
            },
        }

        intent_responses = responses.get(intent, responses[Intent.GENERAL_QUESTION])
        response = intent_responses.get(language, intent_responses.get("en", ""))
        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_education_content(
        self,
        intent: Intent,
        gestational_age_weeks: Optional[int],
        language: str,
    ) -> Optional[str]:
        if intent == Intent.EDUCATION_REQUEST and gestational_age_weeks:
            return self.get_weekly_education(gestational_age_weeks, language)
        return None

    def _simplify_response(self, text: str, channel: str) -> str:
        """Simplify response for SMS/USSD or low literacy."""
        if channel == "ussd":
            # USSD: very short, numbered options
            lines = text.split(". ")
            return ". ".join(lines[:2]) + "."
        if channel == "sms":
            # SMS: under 160 chars
            if len(text) > 155:
                return text[:152] + "..."
        return text

    def _get_suggested_actions(
        self, intent: Intent, language: str
    ) -> List[str]:
        actions: Dict[Intent, Dict[str, List[str]]] = {
            Intent.SYMPTOM_CHECK: {
                "en": ["Describe your symptoms", "Check emergency signs", "Book ANC visit"],
                "sw": ["Elezea dalili zako", "Angalia dalili za dharura", "Panga ziara ya kliniki"],
            },
            Intent.NUTRITION_ADVICE: {
                "en": ["View nutrition guide", "Log your meals", "Get supplement reminders"],
                "sw": ["Angalia mwongozo wa lishe", "Rekodi milo yako"],
            },
            Intent.APPOINTMENT_BOOKING: {
                "en": ["Find nearby clinic", "Set appointment reminder", "View ANC schedule"],
                "sw": ["Tafuta kliniki karibu", "Weka ukumbusho wa miadi"],
            },
        }
        intent_actions = actions.get(intent, {})
        return intent_actions.get(language, intent_actions.get("en", []))

    def _get_follow_up_questions(
        self, intent: Intent, language: str
    ) -> List[str]:
        questions: Dict[Intent, Dict[str, List[str]]] = {
            Intent.SYMPTOM_CHECK: {
                "en": ["How long have you had this symptom?", "Is it getting worse?", "Do you have any other symptoms?"],
                "sw": ["Umekuwa na dalili hii kwa muda gani?", "Inazidi kuwa mbaya?"],
            },
            Intent.EMOTIONAL_SUPPORT: {
                "en": ["Would you like to talk to a counselor?", "Do you have support at home?"],
                "sw": ["Ungependa kuzungumza na mshauri?", "Una msaada nyumbani?"],
            },
            Intent.NUTRITION_ADVICE: {
                "en": ["What foods are available to you?", "Do you have any food allergies?"],
                "sw": ["Ni vyakula gani unavyopata?", "Una mzio wowote wa chakula?"],
            },
        }
        intent_questions = questions.get(intent, {})
        return intent_questions.get(language, intent_questions.get("en", []))

    def _compile_intent_patterns(self) -> Dict[str, List[re.Pattern]]:
        return {
            intent_str: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent_str, patterns in INTENT_PATTERNS.items()
        }

    def _compile_emergency_patterns(self) -> List[re.Pattern]:
        emergency_patterns = INTENT_PATTERNS.get(Intent.EMERGENCY, [])
        return [re.compile(p, re.IGNORECASE) for p in emergency_patterns]


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def create_conversation_ai(api_key: Optional[str] = None) -> ConversationalAI:
    """Create a ConversationalAI instance."""
    return ConversationalAI(mistral_api_key=api_key)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ai = ConversationalAI(mistral_api_key=os.getenv("MISTRAL_API_KEY"))

    test_messages = [
        ("Hello, I am 28 weeks pregnant", "en", "app"),
        ("I have a severe headache and my vision is blurry", "en", "app"),
        ("What should I eat during pregnancy?", "en", "sms"),
        ("Ninajisikia huzuni sana leo", "sw", "whatsapp"),
        ("I am bleeding heavily", "en", "app"),
    ]

    for msg, lang, channel in test_messages:
        print(f"\nUser ({lang}/{channel}): {msg}")
        response = ai.chat(
            session_id="test_session",
            user_message=msg,
            language=lang,
            channel=channel,
            gestational_age_weeks=28,
        )
        print(f"MAMA: {response.message}")
        print(f"  Intent: {response.intent.value} | Emergency: {response.is_emergency}")
        if response.is_emergency:
            print(f"  EMERGENCY TYPE: {response.emergency_type}")
