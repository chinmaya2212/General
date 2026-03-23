import pytest
import os
from typing import Generator

os.environ["JWT_SECRET_KEY"] = "testsecretkey_which_is_over_thirty_two_bytes_long_now"
os.environ["MONGODB_URI"] = "mongodb://localhost"
os.environ["VERTEX_AI_PROJECT"] = "test_project"
os.environ["MISP_URL"] = "https://misp"
os.environ["MISP_API_KEY"] = "key"
os.environ["CISO_ASSISTANT_URL"] = "https://ciso"
os.environ["CISO_ASSISTANT_API_KEY"] = "key"

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
