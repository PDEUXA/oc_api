"""
CRUD operation on DB for interacting with sessions:
- find_session_by_id
- create_session
"""

from typing import Union

from app.core.db import MongoDB, mongodb
from app.schema.sessions import SessionModel


async def find_session_by_id(id: int, mongo: MongoDB = mongodb) -> Union[SessionModel, None]:
    """
    Fetch a session by its id
    :param id: int
    :param mongo: MongoDB
    :return: SessionModel or None if not exist
    """
    if session := await mongo.session_coll.find_one({"id": id}):
        return session


async def create_session(session: SessionModel, mongo: MongoDB = mongodb) -> Union[SessionModel, None]:
    """
    Create a sessions from a SessionModel
    :param session: SessionModel
    :param mongo: MongoDB
    :return: SessionModel or None if session already exist
    """
    if not await mongo.session_coll.find_one({"id": session.id}):
        await mongo.session_coll.insert_one(session.dict())
        return session
