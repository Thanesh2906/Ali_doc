CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    code VARCHAR(40) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id VARCHAR(40) NOT NULL UNIQUE,
    department_id BIGINT REFERENCES departments(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_employees_department_id ON employees(department_id);
CREATE INDEX idx_employees_active ON employees(is_active) WHERE deleted_at IS NULL;

CREATE TABLE employee_profiles (
    id BIGSERIAL PRIMARY KEY,
    employee_uuid UUID NOT NULL REFERENCES employees(id),
    health_profile JSONB NOT NULL DEFAULT '{}'::jsonb,
    emergency_contact JSONB,
    consent_flags JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_employee_profiles_employee_uuid ON employee_profiles(employee_uuid);
CREATE INDEX idx_employee_profiles_health_profile_gin ON employee_profiles USING gin(health_profile);

CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    employee_id VARCHAR(40) NOT NULL,
    session_id VARCHAR(120) NOT NULL,
    title VARCHAR(255),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(employee_id, session_id)
);
CREATE INDEX idx_conversations_employee_id ON conversations(employee_id);
CREATE INDEX idx_conversations_started_at ON conversations(started_at DESC);

CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    token_count INT,
    redacted_content TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_messages_conversation_id_created_at ON messages(conversation_id, created_at DESC);

CREATE TABLE risk_scores (
    id BIGSERIAL PRIMARY KEY,
    employee_id VARCHAR(40) NOT NULL,
    diabetes_risk NUMERIC(5,2) NOT NULL,
    hypertension_risk NUMERIC(5,2) NOT NULL,
    high_claim_risk NUMERIC(5,2) NOT NULL,
    high_absenteeism_risk NUMERIC(5,2) NOT NULL,
    scoring_date DATE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'ml',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(employee_id, scoring_date)
);
CREATE INDEX idx_risk_scores_employee_date ON risk_scores(employee_id, scoring_date DESC);

CREATE TABLE ml_predictions (
    id BIGSERIAL PRIMARY KEY,
    employee_id VARCHAR(40) NOT NULL,
    diabetes_risk NUMERIC(5,2) NOT NULL,
    hypertension_risk NUMERIC(5,2) NOT NULL,
    high_claim_risk NUMERIC(5,2) NOT NULL,
    high_absenteeism_risk NUMERIC(5,2) NOT NULL,
    model_version VARCHAR(60) NOT NULL DEFAULT 'v1',
    input_payload JSONB NOT NULL,
    feature_snapshot JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_ml_predictions_employee_id_created_at ON ml_predictions(employee_id, created_at DESC);
CREATE INDEX idx_ml_predictions_input_payload_gin ON ml_predictions USING gin(input_payload);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_id VARCHAR(120) NOT NULL,
    action VARCHAR(120) NOT NULL,
    resource_type VARCHAR(80) NOT NULL,
    resource_id VARCHAR(120) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_logs_actor_id_created_at ON audit_logs(actor_id, created_at DESC);
