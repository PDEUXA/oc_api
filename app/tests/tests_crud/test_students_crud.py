import asyncio

import pytest

from app.crud.session import create_session, delete_session
from app.crud.student import create_student, \
    find_student_with_id, \
    delete_student, \
    fetch_all_students, get_student_all_sessions, get_distinct
from app.schema.sessions import SessionModel, SessionOutputModel
from app.schema.users import UserModel, UserOutputModel
from app.tests.tests_crud import MockedDoc


class TestStudent(MockedDoc):

    @pytest.fixture(scope="session")
    def event_loop(self):
        return asyncio.get_event_loop()

    @pytest.mark.asyncio
    async def test_create_student(self):
        data = self.multiple_student[0].dict()
        assert UserModel(**data) == await create_student(UserModel(**data), self.mongodb_test)
        assert await create_student(UserModel(**data)) is None
        await delete_student(data["id"], self.mongodb_test)

    @pytest.mark.asyncio
    async def test_find_student_with_id(self):
        data = self.multiple_student[0].dict()
        await create_student(UserModel(**data), self.mongodb_test)
        assert UserOutputModel(**data) == await find_student_with_id(data["id"], self.mongodb_test)
        assert await find_student_with_id(9999) is None
        await delete_student(data["id"], self.mongodb_test)

    @pytest.mark.asyncio
    async def test_fetch_all_students(self):
        response = [UserOutputModel(**student.dict()) for student in self.multiple_student]
        for r in self.multiple_student:
            await create_student(r, self.mongodb_test)
        assert response == await fetch_all_students(self.mongodb_test)
        for r in self.multiple_student:
            await delete_student(r.id, self.mongodb_test)

    @pytest.mark.asyncio
    async def test_delete_student(self):
        data = self.multiple_student[0].dict()

        await create_student(UserModel(**data), self.mongodb_test)
        assert 1 == await delete_student(data["id"], self.mongodb_test)

    @pytest.mark.asyncio
    async def test_get_student_all_sessions(self):
        for s in self.multiple_session:
            await create_session(SessionModel(**s), self.mongodb_test)

        all_7777 = [SessionOutputModel(**session) for session in self.multiple_session
                    if session["recipient"] == 7777]

        assert all_7777 == await get_student_all_sessions(7777, mongo=self.mongodb_test)

        completed_7777 = [SessionOutputModel(**session) for session in self.multiple_session
                          if session["status"] == "completed" and
                          session["recipient"] == 7777]

        assert completed_7777 == await get_student_all_sessions(7777,
                                                                include_status="completed",
                                                                mongo=self.mongodb_test)

        all_7777_except_canceled = [SessionOutputModel(**session) for session in self.multiple_session
                                    if session["status"] != "canceled" and
                                    session["recipient"] == 7777]

        assert all_7777_except_canceled == await get_student_all_sessions(7777,
                                                                          exclude_status="canceled",
                                                                          mongo=self.mongodb_test)

        all_7777_late = [SessionOutputModel(**session) for session in self.multiple_session
                         if session["status"] == "late canceled" and
                         session["recipient"] == 7777]

        assert all_7777_late == await get_student_all_sessions(7777,
                                                               include_status="canceled,late canceled",
                                                               exclude_status="canceled",
                                                               mongo=self.mongodb_test)

        assert await get_student_all_sessions(7777,
                                              include_status="test",
                                              exclude_status="",
                                              mongo=self.mongodb_test) is None

        assert await get_student_all_sessions(8777,
                                              include_status="",
                                              exclude_status="",
                                              mongo=self.mongodb_test) is None
        for s in self.multiple_session:
            await delete_session(s["id"], self.mongodb_test)

    @pytest.mark.asyncio
    async def test_distinct_student(self):
        for s in self.multiple_session:
            await create_session(SessionModel(**s), self.mongodb_test)

        assert [7777, 7778] == await get_distinct(self.mongodb_test)

        for s in self.multiple_session:
            await delete_session(s["id"], self.mongodb_test)
