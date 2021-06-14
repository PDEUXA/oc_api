from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

routes = "students/"


def test_get_student_by_id():
    response = client.get(routes + "7777")
    assert response.status_code == 200
    assert response.json() == {
        "displayName": "TEST",
        "id": 7777,
        "email": "TEST@gmail.com",
        "status": "Auto-financé"
    }

    response = client.get(routes + "984676657631")
    assert response.status_code == 404


def test_add_new_student():
    payload = {
        "displayName": "testPostDisplayName",
        "email": "testPost@gmail.com",
        "enrollment": "",
        "firstName": "testPostFirstName",
        "id": 7778,
        "identityLocked": False,
        "language": "",
        "lastName": "testlastName",
        "openClassroomsProfileUrl": "",
        "organization": "",
        "premium": False,
        "profilePicture": "",
        "status": "testStatus"
    }
    response = client.post(routes, json=payload)
    assert response.status_code == 201
    assert response.json() == payload

    response = client.post(routes, json=payload)
    assert response.status_code == 409


def test_get_student_sessions():
    response = client.get(routes+"7777")
    assert response.status_code == 200
    assert response.json() == {
        "displayName": "TEST",
        "id": 7777,
        "email": "TEST@gmail.com",
        "status": "Auto-financé"
    }

    response = client.get(routes+"7779")
    assert response.status_code == 404
