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
    CAPABILITY_QUERY = "capability_query"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


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
        r"\b(emergency|urgent|dying|ambulance|hospital\s+now)\b",
        r"\b(please\s+help\s+me|someone\s+help|help\s+me\s+i)\b",
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
        # English + Kiswahili — pure greetings only
        r"^(hi|hello|hey|good\s+(morning|afternoon|evening))\b",
        r"^(habari|mambo|hujambo|shikamoo|salama|karibu|salam)\b",
        r"\b(habari\s+yako|habari\s+za\s+asubuhi|habari\s+za\s+jioni)\b",
        r"\b(how\s+are\s+you|nice\s+to\s+meet)\b",
    ],
    Intent.CAPABILITY_QUERY: [
        # Questions about what MAMA can do
        r"\b(what\s+can\s+you\s+do|how\s+can\s+you\s+help|what\s+do\s+you\s+do)\b",
        r"\b(what\s+are\s+you|who\s+are\s+you|tell\s+me\s+about\s+yourself)\b",
        r"\b(what\s+services|what\s+features|what\s+support)\b",
        r"\b(unaweza\s+kunisaidia\s+vipi|unafanya\s+nini|wewe\s+ni\s+nani)\b",
        r"\b(start|begin|nianze|get\s+started)\b",
    ],
}

# ---------------------------------------------------------------------------
# Emergency keywords (multilingual)
# ---------------------------------------------------------------------------

EMERGENCY_KEYWORDS = {
    "en": ["bleeding", "seizure", "unconscious", "not breathing", "cord prolapse",
           "severe pain", "baby not moving", "heavy bleeding", "emergency"],
    "maa": [
        # Bleeding
        "oltau", "nkare oltau", "enkare oltau",
        # Pain
        "enkiama", "enkiama nabo", "enkiama naibor",
        # Emergency / help
        "aidim", "tua", "sopa enkiama",
        # Baby not moving
        "entomononi", "maa entomononi",
        # Seizure
        "enkibolata",
    ],
    "kik": [
        # Bleeding
        "thakame", "thakame nyingi", "gutoka thakame",
        # Pain
        "kurwara", "kuumia",
        # Emergency / help
        "ndiaga", "ndiaga biu", "ndihia",
        # Baby not moving
        "mwana ndaguruka", "mwana ndathii",
        # Seizure / collapse
        "gutingithia", "kugwa",
    ],
    "luo": [
        # Bleeding
        "remo", "remo mathoth", "remo wuok",
        # Pain
        "rem", "rem matek", "chandruok",
        # Emergency / help
        "kony", "kony mapiyo", "chandruok matek",
        # Baby not moving
        "nyathi ok lunge", "nyathi ok miel",
        # Seizure / collapse
        "goyo", "podho piny",
        # Water breaking
        "pi owuok",
    ],
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

# ---------------------------------------------------------------------------
# Maasai cultural maternal health context
# ---------------------------------------------------------------------------

LUO_CULTURAL_CONTEXT = """
Luo (Dholuo) Cultural Context for Maternal Health:
- Luo people (Joluo) live around Lake Victoria in western Kenya and Uganda
- Traditional birth attendants (min nyuol) are highly respected
- The extended family (gweng) plays a central role in pregnancy and birth decisions
- Luo diet: fish (rech) from Lake Victoria, ugali (kuon), vegetables, sorghum — acknowledge these
- Fish is a key protein source — excellent for pregnancy nutrition
- Respect for elders and the husband's family in birth decisions is important
- Postpartum: mother is cared for by female relatives, rests for weeks
- Traditional herbs and practices are common — advise on safety respectfully
- Many Luo women have access to clinics in Kisumu and surrounding areas
- Grief and pregnancy loss are communal — community mourning is important
"""

KIKUYU_CULTURAL_CONTEXT = """
- Kikuyu women (Agikuyu) are from Central Kenya — Mount Kenya region
- Traditional birth attendants (muthiri wa kuhanda) are respected community figures
- The family unit (nyumba) and clan (mbari) are central to decision-making
- Kikuyu diet: githeri (maize+beans), mukimo, irio, sweet potatoes, greens — acknowledge these
- Many Kikuyu women are educated and may mix traditional and modern healthcare
- Respect for elders (athuuri na atumia) is important in health decisions
- Postpartum: mother rests, community brings food (ngwatio) — encourage this
- Traditional herbs (miti shamba) are commonly used — advise safely
- FGC (irua ria atumia) was historically practiced — be sensitive to delivery complications
- Kikuyu women are resourceful and entrepreneurial — empower them with information
- Many live near Nairobi or Central Kenya with reasonable clinic access
"""

MAASAI_CULTURAL_CONTEXT = """
Maasai Cultural Context for Maternal Health:
- Maasai women traditionally give birth at home assisted by elder women (entomononi)
- Respect for elders and traditional birth attendants is paramount
- Cattle and livestock are central to Maasai identity — use relatable analogies
- The community (enkiama) plays a strong role in supporting mothers
- Traditional practices: some are safe, some (like cutting) are harmful — be sensitive but clear
- Maasai diet is rich in milk (enkare), meat, and blood — acknowledge this in nutrition advice
- Many Maasai women may have limited access to formal healthcare facilities
- Encourage clinic visits while respecting traditional values
- Address the husband/family respectfully as decisions are often communal
- Female genital cutting (FGC) is practiced — be aware of complications during delivery
- Postpartum: mothers rest for weeks, supported by community — encourage this
"""

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

    "luo": f"""You are MAMA, a compassionate AI maternal health assistant for the MAMA-LENS platform.
You are speaking with a Luo (Dholuo) woman from western Kenya or Uganda.

LANGUAGE: You MUST respond ENTIRELY in Dholuo (Luo). Every word of your response must be in Dholuo.
If the user writes in English or Swahili, still respond in Dholuo.

{LUO_CULTURAL_CONTEXT}

Your core principles:
- Show deep respect for Luo culture and the role of the extended family
- Reference familiar Luo foods (rech/fish, kuon/ugali) in nutrition advice
- Acknowledge traditional birth attendants (min nyuol) as partners in care
- Be aware of traditional herb use — advise on safety gently
- Celebrate the strength of Luo mothers and their community bonds
- Always encourage ANC visits and skilled birth attendance

Emergency protocol: If you detect ANY emergency, immediately say:
"CHANDRUOK: Dhi ir ospetar ma cok SANI SANI kata luong 999/112."

You are not a doctor. You provide information, support, and guidance.""",

    "kik": f"""You are MAMA, a compassionate AI maternal health assistant for the MAMA-LENS platform.
You are speaking with a Kikuyu (Gikuyu) woman from Kenya.

LANGUAGE: You MUST respond ENTIRELY in Kikuyu (Gĩkũyũ). Every word of your response must be in Kikuyu.
If the user writes in English or Swahili, still respond in Kikuyu.

{KIKUYU_CULTURAL_CONTEXT}

Your core principles:
- Show deep respect for Kikuyu culture and traditions
- Acknowledge traditional birth attendants as partners in care
- Reference familiar Kikuyu foods (githeri, mukimo, irio) in nutrition advice
- Be aware of traditional herb use — advise on safety gently
- Be sensitive to FGC-related complications during delivery
- Empower the woman — Kikuyu women are strong and resourceful
- Always encourage ANC visits and skilled birth attendance
- Address her warmly as "Mwari wa Ngai" (daughter of God) when encouraging

Emergency protocol: If you detect ANY emergency, immediately say:
"HATARI: Nenda kirimu kĩa ũgima kĩa hĩndĩ ĩno RĨRĨA RĨRĨA kana ĩta 999/112."

You are not a doctor. You provide information, support, and guidance.""",

    "maa": f"""You are MAMA, a compassionate AI maternal health assistant for the MAMA-LENS platform.
You are speaking with a Maasai woman.

LANGUAGE: You MUST respond ENTIRELY in Maa (Maasai language). Every word of your response must be in Maa.
If the user writes in English or Swahili, still respond in Maa.

{MAASAI_CULTURAL_CONTEXT}

Your core principles:
- Show deep respect for Maasai culture and traditions
- Acknowledge traditional birth attendants (entomononi) as partners, not obstacles
- Be aware that the nearest clinic may be far — give practical, actionable advice
- Never dismiss traditional practices outright — explain risks gently and respectfully
- Celebrate the strength of Maasai mothers
- Be aware of FGC-related complications — handle with extreme sensitivity
- Always encourage ANC visits and skilled birth attendance

Emergency protocol: If you detect ANY emergency, immediately say:
"ENKIAMA NABO: Naa osupuko kĩa ũgima SIANI SIANI kata ita 999/112."

You are not a doctor. You provide information, support, and guidance.""",

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
        self.api_key = (mistral_api_key or os.getenv("MISTRAL_API_KEY", "")).strip()
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

        # ── Layer 1: Intent Detection ──────────────────────────────────
        intent = self._classify_intent(user_message)

        # ── Layer 2: Risk Classification ───────────────────────────────
        is_emergency, emergency_type = self._check_emergency(user_message, language)
        risk = self._classify_risk(intent, is_emergency)

        if risk == RiskLevel.EMERGENCY:
            intent = Intent.EMERGENCY

        ctx.current_intent = intent
        ctx.risk_level = risk.value

        # ── Layer 3: Response Generation ───────────────────────────────
        education_content = self._get_education_content(
            intent, gestational_age_weeks or ctx.gestational_age_weeks, language
        )

        if risk == RiskLevel.EMERGENCY:
            response_text = self._emergency_response(emergency_type, language)
            requires_handoff = True
            confidence = 1.0
        else:
            response_text, confidence = self._generate_response(
                ctx, user_message, intent, language, literacy_level, channel
            )
            requires_handoff = (
                intent == Intent.EMOTIONAL_SUPPORT and confidence < 0.6
            ) or risk == RiskLevel.HIGH

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

    def _classify_risk(self, intent: Intent, is_emergency: bool) -> RiskLevel:
        """Layer 2: Map intent + emergency flag to a risk level."""
        if is_emergency or intent == Intent.EMERGENCY:
            return RiskLevel.EMERGENCY
        if intent in (Intent.LABOR_SIGNS, Intent.FETAL_MOVEMENT):
            return RiskLevel.HIGH
        if intent in (Intent.SYMPTOM_CHECK, Intent.EMOTIONAL_SUPPORT, Intent.MEDICATION_QUERY):
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _check_emergency(
        self, text: str, language: str
    ) -> Tuple[bool, Optional[str]]:
        """Check for emergency keywords in any supported language.

        Greeting and capability queries are never emergencies regardless
        of incidental keyword overlap.
        """
        # Layer 1 guard: non-emergency intents short-circuit emergency detection
        pre_intent = self._classify_intent(text)
        if pre_intent in (Intent.GREETING, Intent.CAPABILITY_QUERY):
            return False, None

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
        # For indigenous languages: translate input to English, generate response, translate back
        if language == "maa":
            return self._maasai_response(ctx, user_message, intent, literacy_level, channel)
        if language == "kik":
            return self._kikuyu_response(ctx, user_message, intent, literacy_level, channel)
        if language == "luo":
            return self._luo_response(ctx, user_message, intent, literacy_level, channel)

        if self.api_key:
            try:
                return self._mistral_response(ctx, user_message, intent, language, literacy_level, channel)
            except Exception as exc:
                logger.warning("Mistral AI call failed: %s. Using fallback.", exc)

        return self._rule_based_response(intent, language, literacy_level), 0.70

    def _maasai_response(
        self,
        ctx: ConversationContext,
        user_message: str,
        intent: Intent,
        literacy_level: str,
        channel: str,
    ) -> Tuple[str, float]:
        """Send Maasai message directly to Mistral with a Maasai system prompt."""
        if self.api_key:
            try:
                return self._mistral_response(
                    ctx, user_message, intent, "maa", literacy_level, channel
                )
            except Exception as exc:
                logger.warning("Maasai Mistral call failed: %s", exc)
        return self._rule_based_response(intent, "maa", literacy_level), 0.70

    def _luo_response(
        self,
        ctx: ConversationContext,
        user_message: str,
        intent: Intent,
        literacy_level: str,
        channel: str,
    ) -> Tuple[str, float]:
        """Send Luo message directly to Mistral with a Luo system prompt."""
        if self.api_key:
            try:
                return self._mistral_response(
                    ctx, user_message, intent, "luo", literacy_level, channel
                )
            except Exception as exc:
                logger.warning("Luo Mistral call failed: %s", exc)
        return self._rule_based_response(intent, "luo", literacy_level), 0.70

    def _kikuyu_response(
        self,
        ctx: ConversationContext,
        user_message: str,
        intent: Intent,
        literacy_level: str,
        channel: str,
    ) -> Tuple[str, float]:
        """Send Kikuyu message directly to Mistral with a Kikuyu system prompt."""
        if self.api_key:
            try:
                return self._mistral_response(
                    ctx, user_message, intent, "kik", literacy_level, channel
                )
            except Exception as exc:
                logger.warning("Kikuyu Mistral call failed: %s", exc)
        return self._rule_based_response(intent, "kik", literacy_level), 0.70

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
                "en": (
                    "Hello! I'm MAMA, your maternal health companion. 🌸\n\n"
                    "I can support you with:\n"
                    "• Pregnancy and maternal health information\n"
                    "• Nutrition and wellness guidance\n"
                    "• Baby care tips\n"
                    "• Appointment reminders\n"
                    "• Recognising danger signs during pregnancy\n"
                    "• Mental wellness support\n\n"
                    "If you are experiencing severe symptoms such as heavy bleeding, "
                    "difficulty breathing, severe pain, or seizures, please contact "
                    "emergency services (999 / 112) or visit the nearest health facility immediately.\n\n"
                    "How can I support you today?"
                ),
                "sw": (
                    "Habari! Mimi ni MAMA, msaidizi wako wa afya ya uzazi. 🌸\n\n"
                    "Ninaweza kukusaidia na:\n"
                    "• Taarifa za ujauzito na afya ya uzazi\n"
                    "• Mwongozo wa lishe na ustawi\n"
                    "• Vidokezo vya utunzaji wa mtoto\n"
                    "• Ukumbusho wa miadi ya kliniki\n"
                    "• Kutambua dalili za hatari wakati wa ujauzito\n"
                    "• Msaada wa afya ya akili\n\n"
                    "Kama una dalili kali kama damu nyingi, ugumu wa kupumua, "
                    "maumivu makali, au degedege, tafadhali piga simu 999/112 "
                    "au nenda kituo cha afya kilicho karibu mara moja.\n\n"
                    "Ninaweza kukusaidia vipi leo?"
                ),
                "fr": (
                    "Bonjour! Je suis MAMA, votre assistante de sante maternelle. 🌸\n\n"
                    "Je peux vous aider avec:\n"
                    "• Informations sur la grossesse\n"
                    "• Conseils nutritionnels\n"
                    "• Rappels de rendez-vous\n"
                    "• Signes de danger pendant la grossesse\n\n"
                    "En cas d urgence (saignements, convulsions, douleurs severes), "
                    "appelez le 999/112 immediatement.\n\n"
                    "Comment puis-je vous aider aujourd hui?"
                ),
            },
            Intent.CAPABILITY_QUERY: {
                "en": (
                    "I can help with:\n"
                    "• Pregnancy guidance and weekly updates\n"
                    "• Maternal health education\n"
                    "• Nutrition and supplement advice\n"
                    "• Appointment reminders and ANC schedules\n"
                    "• Danger sign awareness\n"
                    "• Baby care information\n"
                    "• Mental wellness and emotional support\n"
                    "• Connecting you to nearby clinics (NHIF/SHA accepted)\n\n"
                    "If you are experiencing severe pain, heavy bleeding, difficulty "
                    "breathing, seizures, or another emergency, please seek medical "
                    "help immediately (999 / 112).\n\n"
                    "How can I support you today?"
                ),
                "sw": (
                    "Ninaweza kukusaidia na:\n"
                    "• Mwongozo wa ujauzito na masasisho ya kila wiki\n"
                    "• Elimu ya afya ya uzazi\n"
                    "• Ushauri wa lishe na virutubisho\n"
                    "• Ukumbusho wa miadi na ratiba ya ANC\n"
                    "• Kutambua dalili za hatari\n"
                    "• Taarifa za utunzaji wa mtoto\n"
                    "• Msaada wa kihisia na afya ya akili\n"
                    "• Kukupata kliniki karibu nawe (NHIF/SHA inakubaliwa)\n\n"
                    "Kama una maumivu makali, damu nyingi, ugumu wa kupumua, "
                    "au dharura nyingine, tafadhali tafuta msaada wa kimatibabu "
                    "mara moja (999 / 112).\n\n"
                    "Ninaweza kukusaidia vipi leo?"
                ),
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
