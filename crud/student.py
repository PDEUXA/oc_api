from typing import Union, List

from core.db import mongodb, MongoDB
from schema.sessions import SessionOutputModel
from schema.users import UserOutputModel, UserModel


async def create_student(student: UserModel, mongo: MongoDB = mongodb):
    """

    :param mongo:
    :param student: Student UserModel
    :return: True for new student, false if student exist
    """
    if await mongo.student_coll.find_one({"id": student.id}):
        return False
    else:
        cursor = await mongo.student_coll.insert_one(student.dict())
        return True


async def get_student_all_sessions(id: int, mongo: MongoDB = mongodb) -> Union[List[SessionOutputModel], None]:
    """
    Get all sessions from an student
    :param mongo:
    :param id: id of the student (int)
    :return:
    """
    cursor = mongo.session_coll.find({"recipient": id})
    sessions = []
    for document in await cursor.to_list(length=100):
        sessions.append(document)
    if sessions:
        return sessions
    else:
        return None


async def get_all_students(mongo: MongoDB = mongodb):
    cursor = mongo.student_coll.find()
    students = []
    for document in await cursor.to_list(length=100):
        students.append(document)
    if students:
        return students


async def get_student_with_id(id: int, mongo: MongoDB = mongodb):
    if student := await mongo.student_coll.find_one({"id": id}):
        return student


async def get_distinct(mongo: MongoDB = mongodb):
    if students_id := await mongo.session_coll.distinct("recipient"):
        return students_id
