import motor.motor_asyncio

from core.config import MONGO_URL
from schema.sessions import SessionModel
from schema.users import UserDetailledModel

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.test


async def post_student(student: UserDetailledModel):
    """

    :param student: Student UserModel
    :return: True for new student, false if student exist
    """
    if cursor := await db["students"].find_one({"id": student.id}):
        return False
    else:
        cursor = await db["students"].insert_one(student.dict())
        return True


async def post_session(session: SessionModel):
    """

    :param student: Student UserModel
    :return: True for new student, false if student exist
    """
    if cursor := await db["sessions"].find_one({"id": session.id}):
        return False
    else:
        cursor = await db["sessions"].insert_one(session.dict())
        return True
