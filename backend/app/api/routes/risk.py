from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.risk import EmployeeRiskInput, RiskPrediction
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/risk", tags=["risk"])
risk_engine = RiskEngine()


@router.post("/predict", response_model=RiskPrediction)
def predict_risk(
    payload: EmployeeRiskInput,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> RiskPrediction:
    result = risk_engine.predict(payload.model_dump())

    db.execute(
        text(
            """
            INSERT INTO ml_predictions (
                employee_id,
                diabetes_risk,
                hypertension_risk,
                high_claim_risk,
                high_absenteeism_risk,
                input_payload
            ) VALUES (
                :employee_id,
                :diabetes_risk,
                :hypertension_risk,
                :high_claim_risk,
                :high_absenteeism_risk,
                :input_payload
            )
            """
        ),
        {**result, "employee_id": payload.employee_id, "input_payload": payload.model_dump_json()},
    )
    db.commit()

    return RiskPrediction(employee_id=payload.employee_id, **result)
