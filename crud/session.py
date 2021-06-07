from core.db import MongoDB, mongodb
from schema.sessions import SessionModel


async def find_session_by_id(id: int, mongo: MongoDB = mongodb):
    if session := await mongo.session_coll.find_one({"id": id}):
        return session


async def create_session(session: SessionModel, mongo: MongoDB = mongodb):
    if await mongo.session_coll.find_one({"id": session.id}):
        return False
    else:
        cursor = await mongo.session_coll.insert_one(session.dict())
        return True
