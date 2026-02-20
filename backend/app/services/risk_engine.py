from pathlib import Path

import joblib
import pandas as pd

from app.core.config import settings


class RiskEngine:
    def __init__(self) -> None:
        self.model = None
        self.feature_columns: list[str] = []
        self._load()

    def _load(self) -> None:
        model_path = Path(settings.model_path)
        features_path = Path(settings.model_features_path)
        if model_path.exists() and features_path.exists():
            self.model = joblib.load(model_path)
            self.feature_columns = joblib.load(features_path)

    def _to_features(self, payload: dict) -> pd.DataFrame:
        raw = {
            "visit_frequency": payload["visit_frequency"],
            "mc_days": payload["mc_days"],
            **{f"condition::{c}": 1 for c in payload["conditions"]},
            **{f"drug::{d}": 1 for d in payload["drug_pattern"]},
            **{f"lab::{l}": 1 for l in payload["lab_flags"]},
        }
        df = pd.DataFrame([raw])
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        return df[self.feature_columns]

    def predict(self, payload: dict) -> dict[str, float]:
        if self.model is None:
            return {
                "diabetes_risk": 0.0,
                "hypertension_risk": 0.0,
                "high_claim_risk": 0.0,
                "high_absenteeism_risk": 0.0,
            }
        features = self._to_features(payload)
        pred = self.model.predict_proba(features)
        return {
            "diabetes_risk": round(float(pred[0][1]) * 100, 2),
            "hypertension_risk": round(float(pred[1][1]) * 100, 2),
            "high_claim_risk": round(float(pred[2][1]) * 100, 2),
            "high_absenteeism_risk": round(float(pred[3][1]) * 100, 2),
        }
