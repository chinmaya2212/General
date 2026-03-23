import pytest
from app.core.config import Settings

def test_settings_validation_failure():
    settings_obj = Settings(
        JWT_SECRET_KEY=None,
        MONGODB_URI=None,
        VERTEX_AI_PROJECT="proj",
        MISP_URL="https://misp",
        MISP_API_KEY="key",
        CISO_ASSISTANT_URL="https://ciso",
        CISO_ASSISTANT_API_KEY="key"
    )
    
    with pytest.raises(ValueError, match="CRITICAL CONFIGURATION ERROR"):
        settings_obj.validate_critical_settings()

def test_settings_validation_success():
    settings_obj = Settings(
        JWT_SECRET_KEY="secret",
        MONGODB_URI="mongodb://localhost",
        VERTEX_AI_PROJECT="proj",
        MISP_URL="https://misp",
        MISP_API_KEY="key",
        CISO_ASSISTANT_URL="https://ciso",
        CISO_ASSISTANT_API_KEY="key"
    )
    
    settings_obj.validate_critical_settings()
