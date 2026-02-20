from pydantic import BaseModel


class EmployeeRiskInput(BaseModel):
    employee_id: str
    conditions: list[str]
    visit_frequency: int
    mc_days: int
    drug_pattern: list[str]
    lab_flags: list[str]


class RiskPrediction(BaseModel):
    employee_id: str
    diabetes_risk: float
    hypertension_risk: float
    high_claim_risk: float
    high_absenteeism_risk: float
