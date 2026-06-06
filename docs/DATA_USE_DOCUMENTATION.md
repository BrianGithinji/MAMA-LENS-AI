# MAMA-LENS AI — Data Use Documentation

**Project:** MAMA-LENS AI (Maternal Assessment & Monitoring for Early Loss Support)
**Version:** 1.0.0
**Date:** 2025

---

## A. Data Sources

### Challenge Datasets from the DASSA Platform

MAMA-LENS AI does not use datasets sourced directly from the DASSA platform. All
datasets used are independently sourced as described below.

---

### Public Datasets Integrated

#### 1. MOTHER Dataset (Primary Conversational AI Training Data)

| Field | Detail |
|---|---|
| Full name | MOTHER: A Maternal Online Technology for Health Care Dataset |
| Source | Harvard Dataverse |
| DOI | https://doi.org/10.7910/DVN/EZLCH3 |
| Reference paper | BMC Research Notes (2025) — https://link.springer.com/article/10.1186/s13104-025-07230-2 |
| Size | 503 validated maternal health question-and-answer pairs |
| Geographic context | Rural and semi-urban Uganda |
| Validation | Answers validated by professional medical personnel |
| Format | JSON (Q&A pairs + intent/pattern/response structures) |
| Purpose in project | Fine-tuning the `google/flan-t5-base` language model (`BrianGithinji/mama-flan-t5`) for maternal health conversational AI |

The dataset is consumed from two files:
- `mother_question_and_answer_pairs_data.json` — 501 direct Q&A pairs
- `mother_intents_patterns_responses_data.json` — intent patterns with canonical responses

---

#### 2. Local Multilingual Training Dataset (Supplementary Conversational AI Data)

| Field | Detail |
|---|---|
| File | `ai/mama_model/training_data.json` |
| Size | ~70 curated input-output pairs |
| Languages | English, Swahili |
| Topics covered | ANC visits, danger signs, nutrition, emotional support, grief, postpartum depression, emergency escalation, fetal movement |
| Origin | Internally authored for MAMA-LENS AI, aligned to WHO ANC guidelines |
| Purpose | Supplements the MOTHER dataset with Swahili-language coverage and Africa-specific clinical guidance |

---

#### 3. Synthetic African Maternal Health Dataset (Risk Model Training Data)

| Field | Detail |
|---|---|
| File | Generated at runtime by `ai/risk-engine/training_pipeline.py` |
| Size | 10,000 samples |
| Format | Tabular (25 features + 1 binary label) |
| Origin | Algorithmically generated — not collected from real patients |
| Distribution basis | Published African population prevalence statistics: 40% anemia prevalence, 15% hypertension, 20% malaria-endemic exposure, 12% HIV prevalence in sub-Saharan Africa, 30% no skilled birth attendant in rural settings |
| Reference | BMC Research Notes (2025) — maternal mortality risk factors in sub-Saharan Africa |
| Purpose | Training the RandomForest + XGBoost ensemble risk classification model |

No real patient data was collected, stored, or used at any stage of model training.

---

## B. Data Management

### Data Cleaning Procedures

**MOTHER Dataset**
- Records with empty `question` or `answer` fields are skipped during loading (`finetune.py`, `_load_mother_dataset()`).
- Whitespace is stripped from all text fields before training.
- Both JSON source files are merged and deduplicated by the loading pipeline.

**Local Training Data**
- Manually curated; no automated cleaning required. All pairs are validated for clinical accuracy before inclusion.

**Synthetic Risk Dataset**
- Continuous features are clipped to physiologically valid ranges at generation time (e.g., hemoglobin clipped to [4, 18] g/dL, systolic BP to [80, 200] mmHg).
- No missing values are possible by construction — all features are programmatically generated.
- A random noise term (σ = 0.04) is added to risk scores before thresholding to prevent perfect label separation and reduce overfitting.

---

### Feature Engineering Methods

The following transformations are applied to the synthetic risk dataset before model training (`FeatureEngineer` class in `training_pipeline.py`):

| Engineered Feature | Method | Rationale |
|---|---|---|
| `bp_product` | systolic × diastolic / 10,000 | Captures joint BP severity |
| `bp_pulse_pressure` | systolic − diastolic | Indicator of arterial stiffness |
| `glucose_bmi_interaction` | glucose × BMI / 1,000 | Combined metabolic risk |
| `anemia_severity` | Ordinal encoding of hemoglobin thresholds (0–3) | WHO anemia severity grades |
| `obstetric_risk_score` | Weighted sum of obstetric history flags | Aggregates prior risk history |
| `lifestyle_risk_score` | Weighted sum of smoking, alcohol, stress, nutrition | Aggregates modifiable risks |
| `symptom_cluster` | Weighted sum of reported symptoms | Headache + vision changes weighted ×2 (preeclampsia triad) |
| `age_risk` | Ordinal encoding: <17 → 2, ≥40 → 2, ≥35 → 1, else 0 | Age-associated obstetric risk |

The base 25 features plus 8 engineered features produce a 33-feature input vector for the ensemble model.

---

### Data Quality Checks

| Check | How it is implemented |
|---|---|
| Clinical threshold validation | Rule-based risk scoring in `risk_engine.py` uses WHO and IADPSG-validated thresholds (e.g., Hb < 11 g/dL for pregnancy anemia, fasting glucose ≥ 92 mg/dL for GDM) |
| Model performance validation | 80/20 train-test split with stratification; 5-fold cross-validated ROC-AUC reported in `training_report.json` |
| Bias analysis across subgroups | `_bias_analysis()` computes AUC separately for four age groups (adolescent 14–17, young adult 18–24, prime 25–34, advanced 35+) and flags underperformance |
| Confidence estimation | When the ML model is unavailable, `_estimate_confidence()` scores assessment confidence based on how many of the six core vital fields (BP, glucose, Hb, weight, height) are provided |
| Emergency override | Regardless of model score, any detected emergency symptom pattern (e.g., severe BP + visual changes, seizure, heavy bleeding) forces `overall_risk_score ≥ 0.85` and `RiskLevel.EMERGENCY` |
| EPDS clinical validation | The Edinburgh Postnatal Depression Scale is scored using the standard validated algorithm (reverse-scored items 1–2, forward-scored items 3–10); scores ≥ 13 map to high risk, ≥ 10 moderate, ≥ 7 mild |

---

## C. Data Governance

### Data Permissions and Licenses

| Dataset | License | Usage Restrictions |
|---|---|---|
| MOTHER Dataset (Harvard Dataverse, DOI: 10.7910/DVN/EZLCH3) | CC0 1.0 Universal (Public Domain Dedication) | No restrictions. Free to use, modify, and redistribute without attribution requirement. Used for non-commercial research and humanitarian healthcare purposes. |
| `google/flan-t5-base` base model (HuggingFace) | Apache 2.0 | Permissive. Allows fine-tuning and commercial use with attribution. |
| Synthetic risk dataset | Not applicable — generated internally | No third-party license applies. |
| Local multilingual training data (`training_data.json`) | MIT License (same as project) | Open. Authored internally. |

The fine-tuned model (`BrianGithinji/mama-flan-t5`) is published on HuggingFace Hub
under the MIT License consistent with the project license.

---

### Privacy Protection Measures

**No real patient data is used or stored in model training.**
All risk model training data is synthetically generated. The conversational AI is
trained exclusively on public domain and internally authored text data.

**Runtime data handling:**
- All API communication is over HTTPS (TLS).
- User authentication uses JWT tokens (HS256) with configurable expiry (default: 60 minutes access, 7 days refresh).
- Passwords are hashed using bcrypt before storage.
- MongoDB Atlas is used with encrypted storage at rest.
- No health assessment data is logged to external services in production (`report_to="none"` in training; Sentry DSN is optional and operator-configured).
- The `.env` file containing all secrets and API keys is excluded from version control via `.gitignore` and is never committed to the repository.
- AWS S3 is used for media storage (configurable); no patient-identifiable media is stored without explicit user action.

**AI model outputs:**
- All risk assessment outputs include a mandatory disclaimer that MAMA-LENS AI is a
  support tool and does not constitute medical advice.
- Bias notes are attached to every `RiskOutput` object, explicitly flagging known
  limitations of the model for adolescent populations and sickle cell disease contexts.

---

### Compliance with Ethical Standards

| Standard | How MAMA-LENS AI complies |
|---|---|
| HIPAA principles | No Protected Health Information (PHI) is stored unencrypted. JWT-secured API, bcrypt-hashed credentials, encrypted database storage. |
| GDPR principles | Users authenticate before any health data is processed. No third-party analytics are bundled by default. Operator must configure any optional external services (Sentry, S3). |
| Kenya Data Protection Act 2019 | Data residency can be configured to `af-south-1` (AWS Africa region). No personal health data is shared with third parties without operator configuration. |
| African Union Data Policy Framework | Data minimisation is applied — only clinically necessary fields are collected for risk assessment. |
| WHO ANC Guidelines (8-contact model) | The `next_assessment_days` logic in `risk_engine.py` follows the WHO recommended antenatal care contact schedule (contacts at <28 weeks, 28–36 weeks, and ≥36 weeks). |
| WHO Anemia Thresholds | Hemoglobin thresholds (< 11 g/dL mild, < 10 g/dL moderate, < 7 g/dL severe) follow WHO criteria for anemia in pregnancy. |
| IADPSG Gestational Diabetes Thresholds | Fasting glucose ≥ 92 mg/dL is used as the GDM screening threshold per International Association of Diabetes and Pregnancy Study Groups criteria. |
| Edinburgh Postnatal Depression Scale (EPDS) | EPDS is implemented using the validated 10-item instrument with standard reverse-scoring. Score interpretation follows published clinical thresholds. |
| Informed use / non-deception | Every session response carries the disclaimer: *"MAMA-LENS AI is a support tool and does not constitute medical advice. Always consult a qualified healthcare provider."* |
| Bias mitigation | Risk thresholds are calibrated to sub-Saharan African population distributions (not Western reference populations). The bias analysis module explicitly monitors AUC performance across age subgroups and documents known gaps (adolescent underrepresentation) in `training_report.json`. Bias notes are surfaced to API consumers in every `RiskOutput`. |

---

*This document should be updated whenever new data sources are integrated or
model training procedures are modified.*
