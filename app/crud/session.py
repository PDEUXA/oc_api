"""
CRUD operation on DB for interacting with sessions:
- find_session_by_id
- create_session
"""
from datetime import datetime, timedelta
from typing import List

from app.core.db import MongoDB, mongodb
from app.schema.sessions import SessionOutModel, SessionModel


async def find_session_by_date(date: datetime, duration: int, mongo: MongoDB = mongodb) -> SessionOutModel:
    """
    Fetch a session by its date between start date + duration and start date -duration
    :param duration: int , duration in minutes
    :param date: datetime
    :param mongo: MongoDB
    :return: SessionOutModel
    """

    if session := await mongo.session_coll.find_one(
            {"sessionDate": {"$lte": date + timedelta(minutes=duration),
                             "$gte": date - timedelta(minutes=duration)},
             "status": "pending"}):
        return SessionOutModel(**session)


async def find_sessions_by_date(date: datetime, mongo: MongoDB = mongodb) -> List[SessionOutModel]:
    """
    Fetch a session by its date between start date + duration and start date -duration
    :param date: datetime
    :param mongo: MongoDB
    :return: SessionOutModel
    """
    if cursor := mongo.session_coll.find(
            {"sessionDate": {"$gte": date},
             "status": "pending"}):
        sessions = []
        for document in await cursor.to_list(length=100):
            sessions.append(document)
        if sessions:
            return [SessionOutModel(**session) for session in sessions]
        else:
            return [SessionOutModel()]


async def find_session_by_id(id: int, mongo: MongoDB = mongodb) -> SessionOutModel:
    """
    Fetch a session by its id
    :param id: int
    :param mongo: MongoDB
    :return: SessionOutModel
    """
    if session := await mongo.session_coll.find_one({"id": id}):
        return SessionOutModel(**session)
    else:
        return SessionOutModel()


async def create_session(session: SessionModel, mongo: MongoDB = mongodb) -> SessionOutModel:
    """
    Create a sessions from a SessionOutModel
    :param session: SessionOutModel
    :param mongo: MongoDB
    :return: SessionOutModel 
    """
    if not await mongo.session_coll.find_one({"id": session.id}):
        await mongo.session_coll.insert_one(session.dict())
    else:
        await mongo.session_coll.update_one({"id": session.id}, {'$set': {'status': session.status}})
    return SessionOutModel(**session.dict())


async def delete_session(id: int, mongo: MongoDB = mongodb) -> int:
    """
    Delete a session in the DB with the corresponding id
    :param id: str
    :param mongo: MongoDB
    :return: Number of session deleted
    """
    session = await mongo.session_coll.delete_one({"id": id})
    return session.deleted_count
