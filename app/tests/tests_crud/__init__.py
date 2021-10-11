from app.core.config import Settings
from app.core.db import MongoDB
from app.schema.users import UserModel


class MockedDoc:
    settings = Settings()
    mongodb_test = MongoDB(settings.MONGO_URL,
                           settings.MONGO_DB,
                           "test_students",
                           "test_sessions",
                           "test_invoices")
    multiple_student = [UserModel(**{"displayName": "testPostDisplayName",
                                     "email": "testPost@gmail.com",
                                     "enrollment": "",
                                     "firstName": "testPostFirstName",
                                     "id": 7779,
                                     "identityLocked": False,
                                     "language": "",
                                     "lastName": "testlastName",
                                     "openClassroomsProfileUrl": "",
                                     "organization": "",
                                     "premium": False,
                                     "profilePicture": "",
                                     "status": "testStatus"}),
                        UserModel(**{"displayName": "testPostDisplayName",
                                     "email": "testPost@gmail.com",
                                     "enrollment": "",
                                     "firstName": "testPostFirstName",
                                     "id": 7777,
                                     "identityLocked": False,
                                     "language": "",
                                     "lastName": "testlastName",
                                     "openClassroomsProfileUrl": "",
                                     "organization": "",
                                     "premium": False,
                                     "profilePicture": "",
                                     "status": "testStatus"})
                        ]

    multiple_session = [
        {
            "projectLevel": "3",
            "id": 9999,
            "recipient": 7777,
            "sessionDate": "2021-05-11T11:00:00Z",
            "lifeCycleStatus": "late canceled test",
            "status": "late canceled",
            "type": "mentoring",
            "videoConference": None
        },
        {
            "projectLevel": "3",
            "id": 9997,
            "recipient": 7777,
            "sessionDate": "2021-05-11T11:00:00Z",
            "lifeCycleStatus": "completed",
            "status": "completed",
            "type": "mentoring",
            "videoConference": None
        },
        {
            "projectLevel": "3",
            "id": 9996,
            "recipient": 7777,
            "sessionDate": "2021-05-11T11:00:00.000",
            "lifeCycleStatus": "canceled",
            "status": "canceled",
            "type": "mentoring",
            "videoConference": None
        },
        {
            "projectLevel": "3",
            "id": 9998,
            "recipient": 7778,
            "sessionDate": "2021-05-11T11:00:00.000",
            "lifeCycleStatus": "late canceled",
            "status": "late canceled",
            "type": "mentoring",
            "videoConference": None
        }]
