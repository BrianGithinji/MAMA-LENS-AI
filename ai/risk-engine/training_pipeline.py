"""
MAMA-LENS AI - ML Training Pipeline
Trains an ensemble model (RandomForest + XGBoost) on synthetic African
maternal health data for risk classification.
"""

from __future__ import annotations

import json
import logging
import os
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import (
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FEATURE_COLUMNS = [
    "age", "gestational_age_weeks", "systolic_bp", "diastolic_bp",
    "blood_glucose", "heart_rate", "hemoglobin", "bmi",
    "previous_miscarriages", "previous_preeclampsia",
    "previous_gestational_diabetes", "previous_preterm_birth",
    "is_multiple_pregnancy", "smoking", "alcohol_use", "stress_level",
    "nutrition_status_encoded", "has_diabetes", "has_hypertension",
    "has_malaria", "has_sickle_cell", "symptom_bleeding",
    "symptom_headache", "symptom_vision_changes", "symptom_swelling",
]

TARGET_COLUMN = "high_risk"  # binary: 0=low/moderate, 1=high/emergency

MODEL_DIR = Path(__file__).parent / "models"

# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

class AfricanMaternalDataGenerator:
    """
    Generates a synthetic dataset representative of African maternal health
    populations, incorporating realistic prevalence rates and distributions.
    """

    def __init__(self, n_samples: int = 10_000, random_state: int = 42) -> None:
        self.n_samples = n_samples
        self.rng = np.random.default_rng(random_state)

    def generate(self) -> pd.DataFrame:
        """Generate synthetic maternal health dataset."""
        n = self.n_samples
        rng = self.rng

        # --- Demographics ---
        # Age distribution: skewed toward 18-35 with tail at extremes
        age = rng.choice(
            np.arange(14, 50),
            size=n,
            p=self._age_distribution(),
        ).astype(float)

        gestational_age = rng.integers(4, 42, size=n).astype(float)

        # --- Vitals ---
        # BP: most normal, ~15% hypertensive in African populations
        systolic_bp = np.clip(rng.normal(118, 18, n), 80, 200)
        diastolic_bp = np.clip(rng.normal(76, 12, n), 50, 130)

        # Hypertensive cases (15%)
        hyp_mask = rng.random(n) < 0.15
        systolic_bp[hyp_mask] = np.clip(rng.normal(148, 15, hyp_mask.sum()), 130, 200)
        diastolic_bp[hyp_mask] = np.clip(rng.normal(96, 10, hyp_mask.sum()), 90, 130)

        # Blood glucose: fasting, mg/dL
        blood_glucose = np.clip(rng.normal(88, 20, n), 60, 300)
        gd_mask = rng.random(n) < 0.08  # 8% GDM prevalence
        blood_glucose[gd_mask] = np.clip(rng.normal(145, 30, gd_mask.sum()), 100, 300)

        heart_rate = np.clip(rng.normal(82, 12, n), 55, 130)

        # Hemoglobin: African women have higher anemia prevalence (~40%)
        hemoglobin = np.clip(rng.normal(11.2, 1.8, n), 5, 16)
        anemia_mask = rng.random(n) < 0.40
        hemoglobin[anemia_mask] = np.clip(rng.normal(9.5, 1.5, anemia_mask.sum()), 5, 11)

        # BMI
        weight_kg = np.clip(rng.normal(65, 14, n), 38, 130)
        height_cm = np.clip(rng.normal(162, 7, n), 140, 190)
        bmi = weight_kg / ((height_cm / 100) ** 2)

        # --- Obstetric history ---
        previous_miscarriages = rng.choice([0, 1, 2, 3, 4], n,
                                            p=[0.65, 0.20, 0.10, 0.03, 0.02])
        previous_preeclampsia = (rng.random(n) < 0.08).astype(int)
        previous_gestational_diabetes = (rng.random(n) < 0.06).astype(int)
        previous_preterm_birth = (rng.random(n) < 0.10).astype(int)
        is_multiple_pregnancy = (rng.random(n) < 0.03).astype(int)

        # --- Lifestyle ---
        smoking = (rng.random(n) < 0.05).astype(int)
        alcohol_use = (rng.random(n) < 0.08).astype(int)
        stress_level = rng.integers(1, 11, n).astype(float)
        nutrition_status_encoded = rng.choice([0, 1, 2, 3], n,
                                               p=[0.15, 0.40, 0.35, 0.10])

        # --- Comorbidities ---
        has_diabetes = (rng.random(n) < 0.05).astype(int)
        has_hypertension = hyp_mask.astype(int)
        has_malaria = (rng.random(n) < 0.20).astype(int)  # endemic regions
        has_sickle_cell = (rng.random(n) < 0.03).astype(int)

        # --- Symptoms ---
        symptom_bleeding = (rng.random(n) < 0.08).astype(int)
        symptom_headache = (rng.random(n) < 0.15).astype(int)
        symptom_vision_changes = (rng.random(n) < 0.05).astype(int)
        symptom_swelling = (rng.random(n) < 0.12).astype(int)

        # --- Label generation (rule-based ground truth) ---
        high_risk = self._generate_labels(
            systolic_bp, diastolic_bp, blood_glucose, hemoglobin, bmi,
            previous_preeclampsia, previous_gestational_diabetes,
            previous_preterm_birth, is_multiple_pregnancy,
            symptom_bleeding, symptom_headache, symptom_vision_changes,
            has_sickle_cell, age,
        )

        df = pd.DataFrame({
            "age": age,
            "gestational_age_weeks": gestational_age,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "blood_glucose": blood_glucose,
            "heart_rate": heart_rate,
            "hemoglobin": hemoglobin,
            "bmi": bmi,
            "previous_miscarriages": previous_miscarriages.astype(float),
            "previous_preeclampsia": previous_preeclampsia.astype(float),
            "previous_gestational_diabetes": previous_gestational_diabetes.astype(float),
            "previous_preterm_birth": previous_preterm_birth.astype(float),
            "is_multiple_pregnancy": is_multiple_pregnancy.astype(float),
            "smoking": smoking.astype(float),
            "alcohol_use": alcohol_use.astype(float),
            "stress_level": stress_level,
            "nutrition_status_encoded": nutrition_status_encoded.astype(float),
            "has_diabetes": has_diabetes.astype(float),
            "has_hypertension": has_hypertension.astype(float),
            "has_malaria": has_malaria.astype(float),
            "has_sickle_cell": has_sickle_cell.astype(float),
            "symptom_bleeding": symptom_bleeding.astype(float),
            "symptom_headache": symptom_headache.astype(float),
            "symptom_vision_changes": symptom_vision_changes.astype(float),
            "symptom_swelling": symptom_swelling.astype(float),
            TARGET_COLUMN: high_risk,
        })

        logger.info(
            "Generated %d samples. High-risk prevalence: %.1f%%",
            n, high_risk.mean() * 100,
        )
        return df

    def _age_distribution(self) -> np.ndarray:
        """Realistic age distribution for African maternal populations."""
        ages = np.arange(14, 50)
        weights = np.exp(-0.5 * ((ages - 26) / 7) ** 2)
        weights[:4] *= 1.5   # slight uptick for teen pregnancies
        weights = weights / weights.sum()
        return weights

    def _generate_labels(
        self,
        systolic_bp: np.ndarray,
        diastolic_bp: np.ndarray,
        blood_glucose: np.ndarray,
        hemoglobin: np.ndarray,
        bmi: np.ndarray,
        previous_preeclampsia: np.ndarray,
        previous_gestational_diabetes: np.ndarray,
        previous_preterm_birth: np.ndarray,
        is_multiple_pregnancy: np.ndarray,
        symptom_bleeding: np.ndarray,
        symptom_headache: np.ndarray,
        symptom_vision_changes: np.ndarray,
        has_sickle_cell: np.ndarray,
        age: np.ndarray,
    ) -> np.ndarray:
        """Generate binary high-risk labels using clinical rules."""
        score = np.zeros(len(systolic_bp))

        score += (systolic_bp >= 160).astype(float) * 3.0
        score += ((systolic_bp >= 140) & (systolic_bp < 160)).astype(float) * 1.5
        score += (diastolic_bp >= 110).astype(float) * 2.5
        score += ((diastolic_bp >= 90) & (diastolic_bp < 110)).astype(float) * 1.0
        score += (blood_glucose >= 140).astype(float) * 1.5
        score += ((blood_glucose >= 92) & (blood_glucose < 140)).astype(float) * 0.5
        score += (hemoglobin < 7.0).astype(float) * 3.0
        score += ((hemoglobin >= 7.0) & (hemoglobin < 10.0)).astype(float) * 1.0
        score += (bmi >= 35).astype(float) * 0.8
        score += previous_preeclampsia.astype(float) * 1.5
        score += previous_gestational_diabetes.astype(float) * 0.8
        score += previous_preterm_birth.astype(float) * 0.8
        score += is_multiple_pregnancy.astype(float) * 1.2
        score += symptom_bleeding.astype(float) * 1.5
        score += (symptom_headache & symptom_vision_changes).astype(float) * 2.0
        score += has_sickle_cell.astype(float) * 1.0
        score += (age >= 40).astype(float) * 0.8
        score += (age < 17).astype(float) * 0.5

        # Add noise
        rng = np.random.default_rng(99)
        score += rng.normal(0, 0.3, len(score))

        return (score >= 2.5).astype(int)


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

class FeatureEngineer:
    """Transforms raw maternal health data into model-ready features."""

    @staticmethod
    def engineer(df: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering transformations."""
        df = df.copy()

        # Interaction features
        df["bp_product"] = df["systolic_bp"] * df["diastolic_bp"] / 10000
        df["bp_pulse_pressure"] = df["systolic_bp"] - df["diastolic_bp"]
        df["glucose_bmi_interaction"] = df["blood_glucose"] * df["bmi"] / 1000
        df["anemia_severity"] = np.where(
            df["hemoglobin"] < 7, 3,
            np.where(df["hemoglobin"] < 10, 2,
                     np.where(df["hemoglobin"] < 11, 1, 0))
        ).astype(float)
        df["obstetric_risk_score"] = (
            df["previous_preeclampsia"] * 2 +
            df["previous_gestational_diabetes"] +
            df["previous_preterm_birth"] +
            df["previous_miscarriages"] * 0.5 +
            df["is_multiple_pregnancy"] * 1.5
        )
        df["lifestyle_risk_score"] = (
            df["smoking"] * 2 +
            df["alcohol_use"] * 2 +
            df["stress_level"] / 5 +
            (3 - df["nutrition_status_encoded"]) * 0.5
        )
        df["symptom_cluster"] = (
            df["symptom_headache"] +
            df["symptom_vision_changes"] * 2 +
            df["symptom_swelling"] +
            df["symptom_bleeding"] * 2
        )
        df["age_risk"] = np.where(
            df["age"] < 17, 2,
            np.where(df["age"] >= 40, 2,
                     np.where(df["age"] >= 35, 1, 0))
        ).astype(float)

        return df

    @staticmethod
    def get_feature_columns(df: pd.DataFrame) -> List[str]:
        """Return all feature columns (excluding target)."""
        return [c for c in df.columns if c != TARGET_COLUMN]


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

@dataclass
class TrainingReport:
    """Stores training results and evaluation metrics."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    n_samples: int = 0
    n_features: int = 0
    train_size: int = 0
    test_size: int = 0
    high_risk_prevalence: float = 0.0
    rf_auc: float = 0.0
    xgb_auc: float = 0.0
    ensemble_auc: float = 0.0
    ensemble_f1: float = 0.0
    ensemble_precision: float = 0.0
    ensemble_recall: float = 0.0
    cv_auc_mean: float = 0.0
    cv_auc_std: float = 0.0
    feature_importances: Dict[str, float] = field(default_factory=dict)
    bias_analysis: Dict[str, Any] = field(default_factory=dict)
    classification_report: str = ""
    confusion_matrix: List[List[int]] = field(default_factory=list)


class MaternalRiskTrainer:
    """
    Trains and evaluates an ensemble model for maternal risk classification.
    """

    def __init__(
        self,
        n_samples: int = 10_000,
        test_size: float = 0.20,
        random_state: int = 42,
        model_dir: Path = MODEL_DIR,
    ) -> None:
        self.n_samples = n_samples
        self.test_size = test_size
        self.random_state = random_state
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> TrainingReport:
        """Execute the full training pipeline."""
        logger.info("=== MAMA-LENS Training Pipeline ===")

        # 1. Generate data
        logger.info("Generating synthetic dataset (%d samples)...", self.n_samples)
        generator = AfricanMaternalDataGenerator(self.n_samples, self.random_state)
        df_raw = generator.generate()

        # 2. Feature engineering
        logger.info("Applying feature engineering...")
        df = FeatureEngineer.engineer(df_raw)
        feature_cols = FeatureEngineer.get_feature_columns(df)

        X = df[feature_cols].values
        y = df[TARGET_COLUMN].values

        # 3. Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size,
            random_state=self.random_state, stratify=y,
        )

        report = TrainingReport(
            n_samples=len(df),
            n_features=len(feature_cols),
            train_size=len(X_train),
            test_size=len(X_test),
            high_risk_prevalence=float(y.mean()),
        )

        # 4. Build models
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=self.random_state,
            n_jobs=-1,
        )

        try:
            from xgboost import XGBClassifier  # type: ignore
            xgb = XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=(y == 0).sum() / (y == 1).sum(),
                random_state=self.random_state,
                eval_metric="logloss",
                verbosity=0,
            )
            estimators = [("rf", rf), ("xgb", xgb)]
            logger.info("Using RandomForest + XGBoost ensemble.")
        except ImportError:
            logger.warning("XGBoost not installed. Using RandomForest only.")
            estimators = [("rf", rf)]

        # 5. Build pipeline with scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 6. Train individual models
        logger.info("Training models...")
        rf.fit(X_train_scaled, y_train)
        rf_proba = rf.predict_proba(X_test_scaled)[:, 1]
        report.rf_auc = float(roc_auc_score(y_test, rf_proba))
        logger.info("RandomForest AUC: %.4f", report.rf_auc)

        if len(estimators) > 1:
            xgb.fit(X_train_scaled, y_train)
            xgb_proba = xgb.predict_proba(X_test_scaled)[:, 1]
            report.xgb_auc = float(roc_auc_score(y_test, xgb_proba))
            logger.info("XGBoost AUC: %.4f", report.xgb_auc)

            # Ensemble: average probabilities
            ensemble_proba = (rf_proba + xgb_proba) / 2
        else:
            ensemble_proba = rf_proba

        # 7. Evaluate ensemble
        ensemble_pred = (ensemble_proba >= 0.5).astype(int)
        report.ensemble_auc = float(roc_auc_score(y_test, ensemble_proba))
        report.ensemble_f1 = float(f1_score(y_test, ensemble_pred))
        report.ensemble_precision = float(precision_score(y_test, ensemble_pred))
        report.ensemble_recall = float(recall_score(y_test, ensemble_pred))
        report.classification_report = classification_report(y_test, ensemble_pred)
        report.confusion_matrix = confusion_matrix(y_test, ensemble_pred).tolist()

        logger.info("Ensemble AUC: %.4f | F1: %.4f | Precision: %.4f | Recall: %.4f",
                    report.ensemble_auc, report.ensemble_f1,
                    report.ensemble_precision, report.ensemble_recall)

        # 8. Cross-validation
        logger.info("Running 5-fold cross-validation...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(rf, X_train_scaled, y_train,
                                     cv=cv, scoring="roc_auc", n_jobs=-1)
        report.cv_auc_mean = float(cv_scores.mean())
        report.cv_auc_std = float(cv_scores.std())
        logger.info("CV AUC: %.4f +/- %.4f", report.cv_auc_mean, report.cv_auc_std)

        # 9. Feature importances
        importances = rf.feature_importances_
        report.feature_importances = {
            col: round(float(imp), 6)
            for col, imp in sorted(
                zip(feature_cols, importances),
                key=lambda x: x[1], reverse=True,
            )
        }

        # 10. Bias analysis
        report.bias_analysis = self._bias_analysis(
            df, feature_cols, scaler, rf, y_test,
            X_test, X_test_scaled,
        )

        # 11. Save models
        self._save_models(rf, scaler, feature_cols)

        # 12. Save report
        self._save_report(report)

        logger.info("Training complete. Models saved to %s", self.model_dir)
        return report

    def _bias_analysis(
        self,
        df: pd.DataFrame,
        feature_cols: List[str],
        scaler: StandardScaler,
        model: RandomForestClassifier,
        y_test: np.ndarray,
        X_test_raw: np.ndarray,
        X_test_scaled: np.ndarray,
    ) -> Dict[str, Any]:
        """Analyze model performance across demographic subgroups."""
        analysis: Dict[str, Any] = {}

        # Age groups
        test_df = df.iloc[-len(y_test):].copy()
        test_df["pred_proba"] = model.predict_proba(X_test_scaled)[:, 1]
        test_df["y_true"] = y_test

        age_groups = {
            "adolescent_14_17": (test_df["age"] < 18),
            "young_adult_18_24": (test_df["age"] >= 18) & (test_df["age"] < 25),
            "prime_25_34": (test_df["age"] >= 25) & (test_df["age"] < 35),
            "advanced_35_plus": (test_df["age"] >= 35),
        }

        age_auc: Dict[str, float] = {}
        for group_name, mask in age_groups.items():
            subset = test_df[mask]
            if len(subset) > 20 and subset["y_true"].nunique() > 1:
                try:
                    group_auc = roc_auc_score(subset["y_true"], subset["pred_proba"])
                    age_auc[group_name] = round(float(group_auc), 4)
                except Exception:
                    age_auc[group_name] = None
            else:
                age_auc[group_name] = None

        analysis["auc_by_age_group"] = age_auc
        analysis["note"] = (
            "Bias analysis across age groups. Lower AUC in adolescent group "
            "may indicate underrepresentation in training data. "
            "Consider collecting more adolescent samples for future retraining."
        )

        return analysis

    def _save_models(
        self,
        model: RandomForestClassifier,
        scaler: StandardScaler,
        feature_cols: List[str],
    ) -> None:
        """Save trained model, scaler, and feature list."""
        try:
            import joblib  # type: ignore
            joblib.dump(model, self.model_dir / "risk_model.joblib")
            joblib.dump(scaler, self.model_dir / "scaler.joblib")
            with open(self.model_dir / "feature_columns.json", "w") as f:
                json.dump(feature_cols, f, indent=2)
            logger.info("Models saved successfully.")
        except ImportError:
            logger.error("joblib not installed. Cannot save models.")

    def _save_report(self, report: TrainingReport) -> None:
        """Save training report as JSON."""
        report_path = self.model_dir / "training_report.json"
        report_dict = {
            "timestamp": report.timestamp,
            "n_samples": report.n_samples,
            "n_features": report.n_features,
            "train_size": report.train_size,
            "test_size": report.test_size,
            "high_risk_prevalence": report.high_risk_prevalence,
            "metrics": {
                "rf_auc": report.rf_auc,
                "xgb_auc": report.xgb_auc,
                "ensemble_auc": report.ensemble_auc,
                "ensemble_f1": report.ensemble_f1,
                "ensemble_precision": report.ensemble_precision,
                "ensemble_recall": report.ensemble_recall,
                "cv_auc_mean": report.cv_auc_mean,
                "cv_auc_std": report.cv_auc_std,
            },
            "top_10_features": dict(
                list(report.feature_importances.items())[:10]
            ),
            "bias_analysis": report.bias_analysis,
            "classification_report": report.classification_report,
            "confusion_matrix": report.confusion_matrix,
        }
        with open(report_path, "w") as f:
            json.dump(report_dict, f, indent=2)
        logger.info("Training report saved to %s", report_path)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    trainer = MaternalRiskTrainer(n_samples=10_000)
    report = trainer.run()
    print("\n=== Training Summary ===")
    print(f"Samples: {report.n_samples} | Features: {report.n_features}")
    print(f"High-risk prevalence: {report.high_risk_prevalence:.1%}")
    print(f"Ensemble AUC:       {report.ensemble_auc:.4f}")
    print(f"Ensemble F1:        {report.ensemble_f1:.4f}")
    print(f"Ensemble Precision: {report.ensemble_precision:.4f}")
    print(f"Ensemble Recall:    {report.ensemble_recall:.4f}")
    print(f"CV AUC:             {report.cv_auc_mean:.4f} +/- {report.cv_auc_std:.4f}")
    print("\nTop 5 Features:")
    for feat, imp in list(report.feature_importances.items())[:5]:
        print(f"  {feat}: {imp:.4f}")
    print("\nBias Analysis:", json.dumps(report.bias_analysis, indent=2))
