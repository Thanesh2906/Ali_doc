from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier

ARTIFACT_DIR = Path("backend/ml/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    expanded = df.copy()
    for col, prefix in [("conditions", "condition"), ("drug_pattern", "drug"), ("lab_flags", "lab")]:
        dummies = expanded[col].explode().str.get_dummies().groupby(level=0).max()
        dummies.columns = [f"{prefix}::{c}" for c in dummies.columns]
        expanded = pd.concat([expanded.drop(columns=[col]), dummies], axis=1)

    expanded = expanded.fillna(0)
    return expanded


def train(data_path: str = "backend/ml/training_data.csv") -> None:
    df = pd.read_csv(data_path)
    features = build_features(
        df[
            [
                "visit_frequency",
                "mc_days",
                "conditions",
                "drug_pattern",
                "lab_flags",
            ]
        ]
    )
    labels = df[
        [
            "diabetes_risk_label",
            "hypertension_risk_label",
            "high_claim_risk_label",
            "high_absenteeism_risk_label",
        ]
    ]

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=42
    )
    model = MultiOutputClassifier(RandomForestClassifier(n_estimators=400, random_state=42))
    model.fit(X_train, y_train)
    print(f"Validation score: {model.score(X_test, y_test):.4f}")

    joblib.dump(model, ARTIFACT_DIR / "risk_model.joblib")
    joblib.dump(features.columns.tolist(), ARTIFACT_DIR / "feature_columns.joblib")


if __name__ == "__main__":
    train()
