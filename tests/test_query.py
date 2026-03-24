from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_query_request_validation():
    response = client.post("/query", json={"question": "hi"})
    assert response.status_code == 422
