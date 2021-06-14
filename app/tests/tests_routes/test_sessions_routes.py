from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_session_by_id():
    response = client.get("/session/9999")
    assert response.status_code == 200
    assert response.json() == {
        "projectLevel": "3",
        "id": 9999,
        "recipient": 7777,
        "sessionDate": "2021-05-11T11:00:00",
        "status": "late canceled",
        "type": "mentoring"
    }

    response = client.get("session/984676657631")
    assert response.status_code == 404
