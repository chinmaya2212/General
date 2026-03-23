import pytest
import pydantic
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

def test_password_hashing():
    password = "supersecretpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token(monkeypatch):
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", pydantic.SecretStr("testsecretkey_which_is_over_thirty_two_bytes_long_now"))
    
    token = create_access_token(subject="user_123")
    assert isinstance(token, str)
    assert len(token) > 20
