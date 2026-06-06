# MAMA-LENS AI — Reproducibility Package

**Project:** MAMA-LENS AI (Maternal Assessment & Monitoring for Early Loss Support)
**Version:** 1.0.0
**Live API:** https://mama-lens-ai.onrender.com
**Live Frontend:** https://mama-lens.netlify.app

---

## Overview

This document provides everything needed to reproduce the main results of
MAMA-LENS AI: the pregnancy risk model, the fine-tuned conversational AI model,
and the live API prototype. No proprietary tools or paid licenses are required
beyond API keys that are freely available.

---

## 1. Scripts and Notebooks

All reproducibility materials are pure Python scripts — no Jupyter environment
is required, though each script can be adapted to a notebook cell-by-cell.

| Script | Location | Purpose |
|---|---|---|
| `training_pipeline.py` | `ai/risk-engine/` | Generates synthetic dataset + trains RandomForest + XGBoost ensemble |
| `risk_engine.py` | `ai/risk-engine/` | Rule-based + ML scoring engine (standalone CLI entry point) |
| `finetune.py` | `ai/mama_model/` | Fine-tunes `google/flan-t5-base` on maternal health Q&A |
| `inference.py` | `ai/mama_model/` | Local inference against the fine-tuned model |
| `emotion_detector.py` | `ai/emotion-ai/` | EPDS scoring + emotion detection (standalone CLI) |
| `conversation_ai.py` | `ai/nlp/` | Conversational AI engine with intent classification (standalone CLI) |
| `train_risk_model.py` | `backend/api/scripts/` | Simplified single-file risk model trainer (backend-scoped) |
| `download_model.py` | `backend/api/scripts/` | Downloads fine-tuned model from HuggingFace Hub at build time |
| `test_api.py` | project root | Tests health check + auth registration against local API |
| `test_risk.py` | project root | Tests risk assessment endpoint against production API |
| `test_model.py` | project root | Tests conversational AI across 6 multilingual prompts against production API |

---

## 2. Model Training Workflow

### 2a. Risk Model (RandomForest + XGBoost Ensemble)

**What it produces:** `ai/risk-engine/models/risk_model.joblib`,
`scaler.joblib`, `feature_columns.json`, `training_report.json`

```
ai/risk-engine/training_pipeline.py
        │
        ▼
AfricanMaternalDataGenerator.generate()
  └─ 10,000 synthetic samples, 25 clinical features
  └─ Labels from rule-based clinical scoring (validated thresholds)
        │
        ▼
FeatureEngineer.engineer()
  └─ 8 interaction/composite features added → 33 total features
        │
        ▼
80 / 20 stratified train-test split
        │
        ├── RandomForestClassifier (200 trees, max_depth=12, balanced weights)
        └── XGBClassifier (200 trees, lr=0.05, scale_pos_weight)
                │
                ▼
        Ensemble: average predicted probabilities
                │
                ▼
        Evaluation: ROC-AUC, F1, Precision, Recall
        5-fold stratified cross-validation
        Bias analysis by age subgroup
                │
                ▼
        Save: risk_model.joblib, scaler.joblib,
              feature_columns.json, training_report.json
```

**Run:**
```bash
cd "d:\MAMA-LENS AI\SYSTEM\ai\risk-engine"
python training_pipeline.py
```

**Expected output** (written to `ai/risk-engine/models/training_report.json`):
```
Ensemble AUC:       ~0.91
Ensemble F1:        ~0.84
Ensemble Precision: ~0.86
Ensemble Recall:    ~0.82
CV AUC:             ~0.90 ± 0.02
```

---

### 2b. Conversational AI — Fine-tuning `mama-flan-t5`

**What it produces:** `ai/mama_model/mama-flan-t5/` (model weights, tokenizer)

```
ai/mama_model/finetune.py
        │
        ▼
load_all_data()
  ├── MOTHER dataset (Harvard Dataverse, 503 validated Q&A pairs)
  │     ├── mother_question_and_answer_pairs_data.json  (501 direct Q&A)
  │     └── mother_intents_patterns_responses_data.json (pattern variants)
  └── training_data.json  (~70 local English + Swahili pairs)
        │
        ▼
Format: {"input": "maternal health: <question>", "output": "<answer>"}
        │
        ▼
AutoTokenizer + AutoModelForSeq2SeqLM (google/flan-t5-base, 247M params)
        │
        ▼
Seq2SeqTrainer
  └─ Epochs: 3 (default)
  └─ Batch size: 4
  └─ Learning rate: 3e-4
  └─ Checkpoints saved every 100 steps
        │
        ▼
Save: ai/mama_model/mama-flan-t5/
  (model.safetensors, config.json, tokenizer.json, tokenizer_config.json)
```

**Install AI dependencies first (separate venv recommended):**
```bash
cd "d:\MAMA-LENS AI\SYSTEM"
python -m venv ai\mama_model\.venv-ai
ai\mama_model\.venv-ai\Scripts\activate
pip install -r ai/requirements-ai.txt
```

**Run fine-tuning:**
```bash
cd "d:\MAMA-LENS AI\SYSTEM\ai\mama_model"
python finetune.py --epochs 3
# With MOTHER dataset (optional, recommended):
# Download from https://doi.org/10.7910/DVN/EZLCH3
# Place files in ai/mama_model/mother_dataset/ then re-run
```

**Estimated time:** ~30 minutes on CPU (3 epochs, ~1,400 examples)

---

## 3. Evaluation Scripts

### 3a. Evaluate the Risk Model

The training pipeline generates a full evaluation report automatically. To
re-evaluate after training:

```bash
cd "d:\MAMA-LENS AI\SYSTEM\ai\risk-engine"
python training_pipeline.py
# Report saved to: ai/risk-engine/models/training_report.json
```

The report includes:
- ROC-AUC (RF, XGBoost, Ensemble)
- F1 Score, Precision, Recall
- 5-fold cross-validated AUC
- Full classification report (per-class)
- Confusion matrix
- Top 10 feature importances
- Bias analysis: AUC by age group (adolescent, young adult, prime, advanced)

To inspect:
```bash
# Windows
type ai\risk-engine\models\training_report.json
```

### 3b. Evaluate the Risk Engine (Rule-Based + ML Combined)

```bash
cd "d:\MAMA-LENS AI\SYSTEM\ai\risk-engine"
python risk_engine.py
```

This runs a built-in sample case (28-week patient with elevated BP,
low hemoglobin, previous preeclampsia, headache + vision changes) and
prints the full `RiskOutput` JSON to stdout including:
- `overall_risk_level`, `overall_risk_score`, `confidence_score`
- Condition-specific scores (preeclampsia, anemia, GDM, miscarriage, preterm)
- `risk_factors` list with weights
- `protective_factors`
- `recommendations` (language-aware)
- `immediate_actions`
- `is_emergency`, `emergency_type`
- `bias_notes`

### 3c. Evaluate the Conversational AI (Local)

```bash
cd "d:\MAMA-LENS AI\SYSTEM\ai\mama_model"
python inference.py
```

Runs 5 test prompts (English + Swahili) through the local fine-tuned model:
```
Input: Hello, I am 20 weeks pregnant
Input: Ninajisikia huzuni sana leo
Input: I have a severe headache and blurred vision
Input: What should I eat during pregnancy?
Input: Mtoto wangu hasogei
```

### 3d. Evaluate the Emotion Detector

```bash
cd "d:\MAMA-LENS AI\SYSTEM\ai\emotion-ai"
python emotion_detector.py
```

Runs 4 test cases (grief, anxiety, crisis, joy in Swahili) and prints:
`primary_emotion`, `distress_level`, `depression_risk`, `crisis_detected`,
`response_tone`, and escalation message where applicable.

### 3e. Evaluate the Conversational AI (Against Live API)

```bash
cd "d:\MAMA-LENS AI\SYSTEM"
python test_model.py
```

Sends 6 prompts (English + Swahili, covering greeting, nutrition, emotional
support, danger signs, emergency, fetal movement) to the production API and
prints `text_response`, `intent`, `is_emergency`, and `emotion_detected` for
each.

### 3f. Evaluate the Risk Assessment Endpoint (Against Live API)

```bash
cd "d:\MAMA-LENS AI\SYSTEM"
python test_risk.py
```

Registers a test user, submits a standard low-risk assessment (28-week,
normal vitals, Swahili language), and prints `risk_level`, `risk_score`,
`is_emergency`, and number of recommendations returned.

---

## 4. Sample Input and Output Files

### 4a. Risk Model — Sample Input

The `RiskInput` used by the CLI entry point in `ai/risk-engine/risk_engine.py`:

```python
{
    "age": 32,
    "gestational_age_weeks": 28,
    "systolic_bp": 148,
    "diastolic_bp": 96,
    "blood_glucose": 105,
    "heart_rate": 88,
    "hemoglobin": 9.8,
    "weight_kg": 72,
    "height_cm": 160,
    "previous_preeclampsia": true,
    "previous_miscarriages": 1,
    "reported_symptoms": ["headache", "swelling_hands", "vision_changes"],
    "language": "en"
}
```

### 4b. Risk Model — Sample Output

```json
{
  "overall_risk_level": "high",
  "overall_risk_score": 0.6842,
  "confidence_score": 0.8167,
  "is_emergency": false,
  "emergency_type": null,
  "preeclampsia_risk_score": 0.82,
  "anemia_risk_score": 0.65,
  "gestational_diabetes_risk_score": 0.18,
  "miscarriage_risk_score": 0.21,
  "preterm_birth_risk_score": 0.24,
  "risk_factors": [
    {
      "factor": "elevated_blood_pressure",
      "weight": 0.30,
      "description": "Blood pressure 148/96 mmHg is above normal range (120/80).",
      "is_modifiable": true
    },
    {
      "factor": "low_hemoglobin",
      "weight": 0.20,
      "description": "Hemoglobin 9.8 g/dL is below the pregnancy threshold of 11 g/dL.",
      "is_modifiable": true
    },
    {
      "factor": "history_of_preeclampsia",
      "weight": 0.20,
      "description": "Previous preeclampsia significantly increases recurrence risk.",
      "is_modifiable": false
    }
  ],
  "recommendations": [
    "Attend all scheduled antenatal care (ANC) visits.",
    "Monitor your blood pressure daily and record readings.",
    "Take iron and folic acid supplements as prescribed."
  ],
  "immediate_actions": [
    "Contact your healthcare provider within 24 hours.",
    "Monitor your blood pressure daily and record readings."
  ],
  "next_assessment_days": 3,
  "bias_notes": [
    "Risk thresholds are calibrated for sub-Saharan African populations..."
  ]
}
```

### 4c. Risk Assessment API — Sample Request

```bash
curl -X POST https://mama-lens-ai.onrender.com/api/v1/risk/assess \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "gestational_age_weeks": 28,
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "blood_glucose": 88,
    "heart_rate": 82,
    "hemoglobin": 11.5,
    "weight_kg": 65,
    "height_cm": 162,
    "previous_miscarriages": 0,
    "stress_level": 4,
    "nutrition_status": "good",
    "language": "sw"
  }'
```

### 4d. Conversational AI API — Sample Request and Response

**Request:**
```bash
curl -X POST https://mama-lens-ai.onrender.com/api/v1/avatar/chat \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a severe headache and blurred vision",
    "language": "en",
    "gestational_age_weeks": 32,
    "session_id": "demo-session"
  }'
```

**Response:**
```json
{
  "text_response": "🚨 URGENT: This sounds like a medical emergency. Please go to the nearest health facility IMMEDIATELY or call emergency services (999 / 112). Do not wait.",
  "intent": "emergency",
  "is_emergency": true,
  "emergency_type": "obstetric_emergency",
  "emotion_detected": "anxiety",
  "suggested_actions": [],
  "education_content": null,
  "requires_human_handoff": true,
  "confidence": 1.0
}
```

### 4e. Conversational AI — Swahili Sample

**Request message:** `"Ninajisikia huzuni sana leo"` (I feel very sad today)

**Response:**
```json
{
  "text_response": "Nakusikia, na hisia zako ni za kweli kabisa. 💚 Ujauzito unaweza kuleta hisia nyingi — furaha, wasiwasi, hofu, na huzuni...",
  "intent": "emotional_support",
  "is_emergency": false,
  "emotion_detected": "sadness",
  "requires_human_handoff": false
}
```

### 4f. EPDS Scoring — Sample Input and Output

```python
# 10 EPDS responses, each scored 0–3
responses = [1, 1, 2, 2, 1, 2, 2, 2, 1, 0]
score, risk_level = score_epds(responses)
# score = 14
# risk_level = "high"  (threshold: ≥13)
```

---

## 5. Instructions for Running the Prototype

### Option A — Live Prototype (No Setup Required)

The full prototype is deployed and accessible now:

| Component | URL |
|---|---|
| Frontend Web App | https://mama-lens.netlify.app |
| Backend API | https://mama-lens-ai.onrender.com |
| Interactive API Docs | https://mama-lens-ai.onrender.com/docs |
| Health Check | https://mama-lens-ai.onrender.com/health |
| AI Model Status | https://mama-lens-ai.onrender.com/debug/ai |

To use the live API directly:
1. Register an account: `POST /api/v1/auth/register`
2. Login to get a JWT token: `POST /api/v1/auth/login`
3. Use the token in the `Authorization: Bearer <token>` header for all subsequent requests

> Note: The Render free tier may take 30–60 seconds to wake from sleep on
> first request. Subsequent requests are fast.

---

### Option B — Run Locally (Full Stack)

#### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11.x |
| Node.js | 18+ |
| Git | Any |
| MongoDB Atlas account | Free tier |
| HuggingFace account | Free (for `HF_API_TOKEN`) |

#### Step 1 — Clone and configure environment

```bash
git clone https://github.com/BrianGithinji/MAMA-LENS-AI.git
cd "MAMA-LENS AI\SYSTEM"

# Copy and fill in the environment file
copy .env.example backend\api\.env
# Minimum required keys to fill in:
#   MONGODB_URI    — from mongodb.com/atlas (free cluster)
#   SECRET_KEY     — any random 32+ character string
#   JWT_SECRET_KEY — any random 32+ character string
#   HF_API_TOKEN   — from huggingface.co/settings/tokens (free)
#   HF_MODEL_ID    — BrianGithinji/mama-flan-t5 (already set in .env.example)
```

#### Step 2 — Run the backend API

```bash
cd backend\api
python -m venv .venv311
.venv311\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`
Health check: `http://localhost:8000/health`

#### Step 3 — Run the frontend

```bash
cd apps\web

# Copy and configure frontend environment
copy .env.example .env
# Set: VITE_API_URL=http://localhost:8000/api/v1

npm install
npm run dev
```

Frontend available at: `http://localhost:5173`

#### Step 4 — Verify everything is working

```bash
# From project root (with backend running):
python test_api.py       # health check + registration test (local)
python test_risk.py      # risk assessment test (targets production by default — edit BASE to localhost)
python test_model.py     # conversational AI test (targets production by default)
```

---

### Option C — Reproduce AI Results Only (No MongoDB Required)

The AI components can be run and evaluated entirely without a database:

```bash
# 1. Train the risk model
cd "d:\MAMA-LENS AI\SYSTEM\ai\risk-engine"
pip install scikit-learn==1.5.0 xgboost==2.0.3 pandas numpy joblib
python training_pipeline.py
# → Prints metrics, saves models to ai/risk-engine/models/

# 2. Run the risk engine CLI
python risk_engine.py
# → Prints full RiskOutput JSON for the built-in sample case

# 3. Test the emotion detector
cd ..\emotion-ai
python emotion_detector.py
# → Runs 4 test cases, prints emotion analysis

# 4. Test the conversational AI (rule-based, no API key needed)
cd ..\nlp
python conversation_ai.py
# → Runs 5 test messages through intent classification + response generation

# 5. Run local model inference (requires transformers + torch)
pip install transformers torch
cd ..\mama_model
python inference.py
# → Loads fine-tuned model from HuggingFace Hub, runs 5 test prompts
```

---

## 6. Project Structure Reference

```
mama-lens-ai/
├── ai/
│   ├── risk-engine/
│   │   ├── training_pipeline.py     ← TRAIN risk model here
│   │   └── risk_engine.py           ← EVALUATE rule-based + ML engine here
│   ├── mama_model/
│   │   ├── finetune.py              ← TRAIN conversational AI here
│   │   ├── inference.py             ← EVALUATE local model here
│   │   ├── training_data.json       ← local multilingual training data
│   │   └── mother_dataset/          ← place MOTHER dataset files here
│   ├── emotion-ai/
│   │   └── emotion_detector.py      ← EVALUATE emotion/EPDS detection here
│   └── nlp/
│       └── conversation_ai.py       ← EVALUATE full conversational AI here
├── backend/api/
│   ├── main.py                      ← FastAPI app entrypoint
│   ├── scripts/
│   │   ├── train_risk_model.py      ← alternative backend-scoped trainer
│   │   └── download_model.py        ← model download at build time
│   └── requirements.txt
├── apps/web/                        ← React frontend
├── test_api.py                      ← API integration test (local)
├── test_risk.py                     ← risk endpoint test (production)
└── test_model.py                    ← conversational AI test (production)
```

---

## 7. Key Environment Variables for Reproduction

| Variable | Required for | Where to get |
|---|---|---|
| `HF_API_TOKEN` | Conversational AI inference via HF API | huggingface.co/settings/tokens |
| `HF_MODEL_ID` | Identifies model (`BrianGithinji/mama-flan-t5`) | Already set in `.env.example` |
| `MONGODB_URI` | Full API + risk assessment persistence | mongodb.com/atlas (free) |
| `SECRET_KEY` | JWT auth | Any 32+ char random string |
| `JWT_SECRET_KEY` | JWT signing | Any 32+ char random string |
| `MISTRAL_API_KEY` | Optional: richer conversational responses | console.mistral.ai |

Risk model training (`training_pipeline.py`) and all AI module CLI entry points
require **no API keys** and run fully offline.

---

*For questions about reproducing specific results, refer to the inline docstrings
in each script or open an issue on the GitHub repository.*
