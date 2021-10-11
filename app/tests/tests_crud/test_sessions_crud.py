import asyncio
from datetime import datetime

import pytest

from app.crud.session import create_session, delete_session, find_session_by_id, find_session_by_date
from app.schema.sessions import SessionModel, SessionOutModel
from app.tests.tests_crud import MockedDoc


class TestSession(MockedDoc):

    @pytest.fixture(scope="session")
    def event_loop(self):
        return asyncio.get_event_loop()

    @pytest.mark.asyncio
    async def test_create_session(self):
        data = self.multiple_session[0]
        assert SessionOutModel(**data) == await create_session(SessionModel(**data), self.mongodb_test)
        assert SessionOutModel(**data) == await create_session(SessionModel(**data), self.mongodb_test)
        await delete_session(data["id"], self.mongodb_test)

    @pytest.mark.asyncio
    async def test_delete_session(self):
        data = self.multiple_session[0]
        await create_session(SessionModel(**data), self.mongodb_test)
        assert 1 == await delete_session(data["id"], self.mongodb_test)

    @pytest.mark.asyncio
    async def test_find_session_with_id(self):
        data = self.multiple_session[0]
        await create_session(SessionModel(**data), self.mongodb_test)
        assert SessionOutModel(**data) == await find_session_by_id(data["id"], self.mongodb_test)
        assert SessionOutModel() == await find_session_by_id(99, self.mongodb_test)
        await delete_session(data["id"], self.mongodb_test)

    @pytest.mark.asyncio
    async def test_find_session_with_date(self):
        data = SessionModel(**self.multiple_session[0])
        await create_session(data, self.mongodb_test)
        assert SessionOutModel(**data.dict()) == await find_session_by_date(data.sessionDate.isoformat(),
                                                                            self.mongodb_test)
        await delete_session(data["id"], self.mongodb_test)
