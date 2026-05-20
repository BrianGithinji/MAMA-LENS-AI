"""
MAMA-LENS AI — Risk Model Training Script
Based on: BMC Research Notes (2025) - Maternal mortality risk factors in sub-Saharan Africa
https://link.springer.com/article/10.1186/s13104-025-07230-2

Features validated by the paper:
- Hypertensive disorders (top predictor)
- Anemia / hemoglobin
- Referral delay / facility distance (top mortality predictor)
- ANC attendance < 4 visits
- Skilled birth attendant absence
- Grand multiparity (>=5)
- HIV status
- PPH history
- Random Forest confirmed as best model (AUC ~0.89)

Run from backend/api/:
    python scripts/train_risk_model.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent.parent / "app" / "models" / "risk_model.joblib"
N_SAMPLES = 10000
RANDOM_SEED = 42

FEATURE_NAMES = [
    "age", "gestational_weeks", "systolic_bp", "diastolic_bp", "blood_glucose",
    "heart_rate", "hemoglobin", "bmi", "prev_miscarriages", "prev_preeclampsia",
    "prev_gd", "prev_preterm", "prev_pph", "multiple_preg", "parity",
    "anc_visits", "skilled_birth_attendant", "facility_distance_km",
    "smoking", "alcohol", "stress_level", "nutrition",
    "has_diabetes", "has_hypertension", "has_malaria", "has_sickle_cell", "has_hiv",
    "has_bleeding", "has_headache", "has_vision_changes",
]


def generate_dataset(n: int, seed: int) -> tuple:
    """
    Generate synthetic African maternal health dataset (30 features).
    Feature order must match RiskInput._extract_features() exactly.
    Labels: 0 = low/moderate risk, 1 = high/emergency risk
    """
    rng = np.random.default_rng(seed)

    # Demographics
    age               = rng.integers(15, 46, n).astype(float)
    gestational_weeks = rng.integers(4, 42, n).astype(float)

    # Vitals — sub-Saharan Africa distributions
    systolic_bp   = rng.normal(118, 18, n).clip(70, 200)
    diastolic_bp  = rng.normal(76, 12, n).clip(45, 130)
    blood_glucose = rng.normal(88, 22, n).clip(50, 300)
    heart_rate    = rng.normal(82, 14, n).clip(50, 160)
    hemoglobin    = rng.normal(10.5, 2.0, n).clip(4, 18)   # lower baseline in Africa
    bmi           = rng.normal(24.0, 5.5, n).clip(14, 50)

    # Obstetric history
    prev_miscarriages = rng.choice([0,1,2,3], n, p=[0.60,0.22,0.12,0.06]).astype(float)
    prev_preeclampsia = rng.choice([0,1], n, p=[0.88,0.12]).astype(float)
    prev_gd           = rng.choice([0,1], n, p=[0.90,0.10]).astype(float)
    prev_preterm      = rng.choice([0,1], n, p=[0.87,0.13]).astype(float)
    prev_pph          = rng.choice([0,1], n, p=[0.92,0.08]).astype(float)   # paper
    multiple_preg     = rng.choice([0,1], n, p=[0.96,0.04]).astype(float)
    parity            = rng.choice([0,1,2,3,4,5,6], n,
                                   p=[0.20,0.22,0.22,0.16,0.10,0.06,0.04]).astype(float)

    # Paper-validated access factors
    anc_visits             = rng.choice([0,1,2,3,4,5,6,7,8], n,
                                        p=[0.05,0.08,0.12,0.15,0.20,0.15,0.12,0.08,0.05]).astype(float)
    skilled_birth_attendant = rng.choice([0,1], n, p=[0.30,0.70]).astype(float)  # 30% no SBA in rural Africa
    facility_distance_km   = rng.exponential(8, n).clip(0, 100)                  # skewed — many far

    # Lifestyle
    smoking      = rng.choice([0,1], n, p=[0.92,0.08]).astype(float)
    alcohol      = rng.choice([0,1], n, p=[0.85,0.15]).astype(float)
    stress_level = rng.integers(1, 11, n).astype(float)
    nutrition    = rng.choice([0,1,2,3], n, p=[0.20,0.35,0.30,0.15]).astype(float)

    # Conditions
    has_diabetes     = rng.choice([0,1], n, p=[0.92,0.08]).astype(float)
    has_hypertension = rng.choice([0,1], n, p=[0.85,0.15]).astype(float)
    has_malaria      = rng.choice([0,1], n, p=[0.80,0.20]).astype(float)
    has_sickle_cell  = rng.choice([0,1], n, p=[0.95,0.05]).astype(float)
    has_hiv          = rng.choice([0,1], n, p=[0.88,0.12]).astype(float)   # paper: ~12% in SSA

    # Symptoms
    has_bleeding      = rng.choice([0,1], n, p=[0.88,0.12]).astype(float)
    has_headache      = rng.choice([0,1], n, p=[0.75,0.25]).astype(float)
    has_vision_changes = rng.choice([0,1], n, p=[0.90,0.10]).astype(float)

    X = np.column_stack([
        age, gestational_weeks, systolic_bp, diastolic_bp, blood_glucose,
        heart_rate, hemoglobin, bmi, prev_miscarriages, prev_preeclampsia,
        prev_gd, prev_preterm, prev_pph, multiple_preg, parity,
        anc_visits, skilled_birth_attendant, facility_distance_km,
        smoking, alcohol, stress_level, nutrition,
        has_diabetes, has_hypertension, has_malaria, has_sickle_cell, has_hiv,
        has_bleeding, has_headache, has_vision_changes,
    ])

    # ---------------------------------------------------------------------------
    # Label generation — paper-validated clinical rules
    # ---------------------------------------------------------------------------
    risk_score = np.zeros(n)

    # Hypertension — paper: top predictor
    risk_score += np.where(systolic_bp >= 160, 0.55, 0.0)
    risk_score += np.where((systolic_bp >= 140) & (systolic_bp < 160), 0.30, 0.0)
    risk_score += np.where(diastolic_bp >= 110, 0.45, 0.0)
    risk_score += np.where((diastolic_bp >= 90) & (diastolic_bp < 110), 0.20, 0.0)

    # Anemia — paper: major predictor
    risk_score += np.where(hemoglobin < 7.0,  0.50, 0.0)
    risk_score += np.where((hemoglobin >= 7.0) & (hemoglobin < 10.0), 0.28, 0.0)
    risk_score += np.where((hemoglobin >= 10.0) & (hemoglobin < 11.0), 0.12, 0.0)

    # Glucose
    risk_score += np.where(blood_glucose >= 140, 0.28, 0.0)
    risk_score += np.where((blood_glucose >= 92) & (blood_glucose < 140), 0.10, 0.0)

    # Paper: referral delay / facility distance = top mortality predictor
    risk_score += np.where(facility_distance_km > 20, 0.25, 0.0)
    risk_score += np.where((facility_distance_km > 10) & (facility_distance_km <= 20), 0.15, 0.0)
    risk_score += np.where((facility_distance_km > 5) & (facility_distance_km <= 10), 0.08, 0.0)

    # Paper: no skilled birth attendant
    risk_score += (1 - skilled_birth_attendant) * 0.22

    # Paper: ANC < 4 visits
    risk_score += np.where(anc_visits < 4, 0.18, 0.0)
    risk_score += np.where(anc_visits < 2, 0.10, 0.0)  # extra penalty

    # Obstetric history
    risk_score += prev_preeclampsia * 0.20
    risk_score += prev_pph * 0.18           # paper: PPH history
    risk_score += prev_gd * 0.12
    risk_score += prev_preterm * 0.15
    risk_score += multiple_preg * 0.18
    risk_score += prev_miscarriages * 0.08
    risk_score += np.where(parity >= 5, 0.15, 0.0)   # paper: grand multiparity

    # Symptoms
    risk_score += has_bleeding * 0.20
    risk_score += has_vision_changes * 0.18
    risk_score += has_headache * 0.08

    # Conditions
    risk_score += has_diabetes * 0.10
    risk_score += has_hypertension * 0.15
    risk_score += has_malaria * 0.10
    risk_score += has_sickle_cell * 0.12
    risk_score += has_hiv * 0.10            # paper: HIV significant in SSA

    # Lifestyle
    risk_score += smoking * 0.08
    risk_score += alcohol * 0.08
    risk_score += np.where(stress_level >= 8, 0.08, 0.0)

    # Age extremes
    risk_score += np.where(age >= 40, 0.12, 0.0)
    risk_score += np.where(age < 18, 0.10, 0.0)

    # Noise
    risk_score += rng.normal(0, 0.04, n)
    risk_score = risk_score.clip(0, 1)

    y = (risk_score >= 0.40).astype(int)
    logger.info("Dataset: %d samples | High risk: %d (%.1f%%)", n, y.sum(), 100 * y.mean())
    return X, y


def train():
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split, cross_val_score
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        from sklearn.metrics import classification_report, roc_auc_score
        import joblib
    except ImportError as e:
        logger.error("Missing: %s — run: pip install scikit-learn joblib", e)
        sys.exit(1)

    logger.info("Generating dataset (%d samples, 30 features)...", N_SAMPLES)
    X, y = generate_dataset(N_SAMPLES, RANDOM_SEED)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )),
    ])

    logger.info("Training Random Forest (300 trees, 30 features)...")
    pipeline.fit(X_train, y_train)

    y_pred  = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    logger.info("\n%s", classification_report(y_test, y_pred,
                target_names=["Low/Moderate", "High/Emergency"]))
    logger.info("ROC-AUC: %.4f", roc_auc_score(y_test, y_proba))

    cv = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc", n_jobs=-1)
    logger.info("5-fold CV ROC-AUC: %.4f +/- %.4f", cv.mean(), cv.std())

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info("Model saved -> %s", MODEL_PATH)

    rf = pipeline.named_steps["clf"]
    importances = sorted(zip(FEATURE_NAMES, rf.feature_importances_),
                         key=lambda x: x[1], reverse=True)
    logger.info("\nTop 10 feature importances (paper validation):")
    for name, imp in importances[:10]:
        logger.info("  %-30s %.4f", name, imp)


if __name__ == "__main__":
    train()
