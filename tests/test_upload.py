from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_upload_rejects_unsupported_file():
    response = client.post(
        "/upload",
        files={"file": ("bad.csv", BytesIO(b"a,b,c"), "text/csv")},
    )
    assert response.status_code == 400
