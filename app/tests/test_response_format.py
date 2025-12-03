from fastapi.testclient import TestClient
from app.main import app
from app.schemas.response import APIResponse

client = TestClient(app)

def test_health_check_response_format():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Health check passed"
    assert data["data"]["status"] == "ok"

def test_root_response_format():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Welcome" in data["message"]

def test_validation_error_format():
    # Trigger a validation error
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "Validation failed"
    assert "meta" in data
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_404_error_format():
    response = client.get("/api/v1/non-existent")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "meta" in data
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"

def test_403_error_format():
    # Try to access a protected endpoint without token
    response = client.get("/api/v1/amenities/")
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert "meta" in data
    assert "error" in data
    assert data["error"]["code"] == "HTTP_403"
