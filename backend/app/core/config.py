from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ali Doctor API"
    environment: str = "development"
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://ali:ali@db:5432/ali_doctor"
    model_path: str = "ml/artifacts/risk_model.joblib"
    model_features_path: str = "ml/artifacts/feature_columns.joblib"
    medical_disclaimer: str = (
        "Ali Doctor is an AI assistant for wellness guidance only and is not a "
        "replacement for licensed clinical diagnosis or emergency care."
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
