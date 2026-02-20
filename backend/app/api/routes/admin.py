from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard-metrics")
def dashboard_metrics(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> dict:
    risk_distribution = db.execute(
        text(
            """
            SELECT
              CASE
                WHEN high_claim_risk >= 80 THEN 'critical'
                WHEN high_claim_risk >= 60 THEN 'high'
                WHEN high_claim_risk >= 30 THEN 'moderate'
                ELSE 'low'
              END AS risk_band,
              COUNT(*) AS count
            FROM ml_predictions
            GROUP BY risk_band
            """
        )
    ).mappings().all()

    trend = db.execute(
        text(
            """
            SELECT to_char(date_trunc('week', created_at), 'YYYY-MM-DD') AS week,
                   AVG(high_claim_risk) AS avg_risk
            FROM ml_predictions
            GROUP BY week
            ORDER BY week
            """
        )
    ).mappings().all()

    mc_vs_risk = db.execute(
        text(
            """
            SELECT (input_payload->>'mc_days')::int AS mc_days,
                   high_claim_risk AS risk
            FROM ml_predictions
            WHERE input_payload ? 'mc_days'
            LIMIT 500
            """
        )
    ).mappings().all()

    department_heatmap = db.execute(
        text(
            """
            SELECT d.name AS department_name,
                   'high_claim_risk' AS risk_band,
                   ROUND(AVG(m.high_claim_risk), 2) AS value
            FROM ml_predictions m
            JOIN employees e ON e.employee_id = m.employee_id
            JOIN departments d ON d.id = e.department_id
            GROUP BY d.name
            ORDER BY value DESC
            """
        )
    ).mappings().all()

    top_employees = db.execute(
        text(
            """
            SELECT employee_id, high_claim_risk
            FROM ml_predictions
            ORDER BY high_claim_risk DESC
            LIMIT 10
            """
        )
    ).mappings().all()

    return {
        "risk_distribution": risk_distribution,
        "risk_trend": trend,
        "mc_vs_risk": mc_vs_risk,
        "department_heatmap": department_heatmap,
        "top_high_risk_employees": top_employees,
    }
