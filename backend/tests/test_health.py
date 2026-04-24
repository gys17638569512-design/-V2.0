from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_unified_response() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "service": "dmms-backend",
            "status": "ok",
        },
    }
