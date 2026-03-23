from typing import List, Union, Any, Optional
from pydantic import field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Security Intelligence Platform MVP"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    
    CORS_ORIGINS: List[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return v
        return []

    LOG_LEVEL: str = "INFO"
    MAX_REQUEST_SIZE: int = 5242880  # 5MB

    # Secrets - Load from Env
    JWT_SECRET_KEY: Optional[SecretStr] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    MONGODB_URI: Optional[SecretStr] = None
    MONGODB_DB_NAME: str = "ai_sec_intel"

    VERTEX_AI_PROJECT: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_MODEL: str = "gemini-2.5-flash"

    MISP_URL: Optional[str] = None
    MISP_API_KEY: Optional[SecretStr] = None

    CISO_ASSISTANT_URL: Optional[str] = None
    CISO_ASSISTANT_API_KEY: Optional[SecretStr] = None

    def validate_critical_settings(self):
        missing = []
        if not self.JWT_SECRET_KEY: missing.append("JWT_SECRET_KEY")
        if not self.MONGODB_URI: missing.append("MONGODB_URI")
        if not self.VERTEX_AI_PROJECT: missing.append("VERTEX_AI_PROJECT")
        if not self.MISP_URL: missing.append("MISP_URL")
        if not self.MISP_API_KEY: missing.append("MISP_API_KEY")
        if not self.CISO_ASSISTANT_URL: missing.append("CISO_ASSISTANT_URL")
        if not self.CISO_ASSISTANT_API_KEY: missing.append("CISO_ASSISTANT_API_KEY")
        
        if missing:
            raise ValueError(f"CRITICAL CONFIGURATION ERROR: Missing required environment variables: {', '.join(missing)}")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
