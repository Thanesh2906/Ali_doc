# Ali Doctor — Production-Ready AI Healthcare Chat System Blueprint

## 1) High-Level Architecture Diagram

```text
┌─────────────────────────────── Frontend (React) ───────────────────────────────┐
│ WhatsApp-style Chat UI | Admin Analytics Dashboard | JWT in Authorization header│
└───────────────────────────────┬──────────────────────────────────────────────────┘
                                │ HTTPS
                        ┌───────▼────────┐
                        │ FastAPI Gateway │
                        │ /auth /chat     │
                        │ /risk /admin    │
                        └───┬─────────┬───┘
                            │         │
        ┌───────────────────▼───┐   ┌─▼────────────────────┐
        │ Conversation Memory    │   │ ML Risk Engine       │
        │ - Session memory       │   │ - MultiOutput RF     │
        │ - Long-term history    │   │ - Predict 4 risks    │
        └────────────┬───────────┘   └──────────┬───────────┘
                     │                          │
            ┌────────▼────────┐        ┌────────▼────────┐
            │ PostgreSQL       │        │ Model Artifacts │
            │ messages, risks, │        │ joblib files    │
            │ audit logs, etc. │        │ + feature list  │
            └──────────────────┘        └─────────────────┘
```

## 2) Clean Folder Structure

```text
backend/
  app/
    api/routes/{auth,chat,risk,admin}.py
    core/{config,security}.py
    db/session.py
    schemas/{auth,chat,risk}.py
    services/{memory,llm,risk_engine}.py
    main.py
  ml/train_risk_model.py
  requirements.txt
frontend/
  src/
    components/{ChatWindow,AdminDashboard}.jsx
    api/client.js
    styles/app.css
    App.jsx
    main.jsx
database/schema.sql
docker-compose.yml
README.md
```

## 3) Conversation Memory Design

- `conversations`: one record per employee + session.
- `messages`: role-based (`user`, `assistant`, `system`) chronological message store.
- Context retrieval before every LLM call uses `context_window` limit.
- Prompt assembly injects historical turns + latest question.

### Prompt Injection Flow
1. Upsert conversation for `(employee_id, session_id)`.
2. Fetch latest N messages ordered by timestamp.
3. Build role-aware prompt.
4. Call LLM provider.
5. Persist user + assistant messages.

## 4) ML Predictive Risk Engine

### Feature Engineering
- Numeric: `visit_frequency`, `mc_days`.
- Multi-hot encoded categorical arrays:
  - `conditions` => `condition::<value>`
  - `drug_pattern` => `drug::<value>`
  - `lab_flags` => `lab::<value>`

### Labels
- `diabetes_risk_label`
- `hypertension_risk_label`
- `high_claim_risk_label`
- `high_absenteeism_risk_label`

### Model
- `MultiOutputClassifier(RandomForestClassifier)`.
- Saves:
  - `risk_model.joblib`
  - `feature_columns.joblib`

### FastAPI Prediction Pipeline
- `/api/v1/risk/predict` receives employee payload.
- Feature transform aligns to training columns.
- Returns `%` probabilities for each risk.
- Stores prediction for analytics.

## 5) Dashboard Visualization

Implemented with `Recharts`:
- Workforce Risk Distribution (Pie)
- Risk Trend Over Time (Line)
- MC Days vs Risk Correlation (Scatter)
- Department Risk Heatmap (custom card heatmap)
- Top 10 High-Risk Employees (Bar)

API: `/api/v1/admin/dashboard-metrics`
- Aggregates risk bands, trends, MC correlation, department heatmap values, top employees.

## 6) Security, Privacy, Compliance

- JWT auth (`/api/v1/auth/login`) for secured endpoints.
- Medical disclaimer returned in chat response.
- Audit logging table for admin and sensitive actions.
- Soft-deletes to preserve data lineage.
- Privacy strategy:
  - Encrypt PHI at rest + in transit.
  - Role-based access control (admin, clinician, employee).
  - PII minimization and tokenization for AI prompts.
  - Retention policy + right-to-erasure workflows.

## 7) Deployment Plan (Docker)

1. `docker compose up --build`
2. Postgres boots and applies `database/schema.sql`.
3. Backend on `:8000`.
4. Frontend on `:5173`.

## 8) Scalability Recommendations

- Introduce Redis for short-lived conversation cache.
- Add async queue (Celery/RQ) for model retraining and heavy analytics.
- Partition `messages` and `ml_predictions` by month.
- Add API gateway + rate limiting + WAF.
- Use vector DB for semantic memory retrieval.

## 9) Future Upgrades

- Replace placeholder LLM service with OpenAI/Azure + safety guardrails.
- Add RAG over corporate medical policies and insurance SOP docs.
- Add explainable AI layer (SHAP) for risk outcomes.
- Add federated learning and drift monitoring dashboards.
