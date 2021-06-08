"""
CRUD operation on DB for interacting with sessions:
- get_student_all_sessions
- create_student
- fetch_all_students
- find_student_with_id
- get_distinct
"""

from typing import Union, List

from app.core.db import mongodb, MongoDB
from app.schema.sessions import SessionOutputModel
from app.schema.users import UserModel, UserOutputModel


async def create_student(student: UserModel, mongo: MongoDB = mongodb):
    """

    :param mongo:
    :param student: Student UserModel
    :return: True for new student, false if student exist
    """
    if not await mongo.student_coll.find_one({"id": student.id}):
        await mongo.student_coll.insert_one(student.dict())
        return student


async def get_student_all_sessions(id: int,
                                   mongo: MongoDB = mongodb) -> Union[List[SessionOutputModel], None]:
    """
    Get all sessions from an student from DB
    :param mongo: MongoDB
    :param id: id of the student (int)
    :return: List of SessionOutputModel or None if student has no session
    """
    cursor = mongo.session_coll.find({"recipient": id})
    sessions = []
    for document in await cursor.to_list(length=100):
        sessions.append(document)
    if sessions:
        return sessions


async def fetch_all_students(mongo: MongoDB = mongodb) -> Union[List[UserOutputModel], None]:
    """
    Fetch all students from DB
    :param mongo: MongoDB
    :return: list of UserOutputModel or None if no students in DB
    """
    cursor = mongo.student_coll.find()
    students = []
    for document in await cursor.to_list(length=100):
        students.append(document)
    if students:
        return students


async def find_student_with_id(id: int, mongo: MongoDB = mongodb) -> Union[UserOutputModel, None]:
    """
    Fetch a student from DB according to its id
    :param id: int
    :param mongo: MongoDB
    :return: UserOutputModel or None if student does not exist
    """
    if student := await mongo.student_coll.find_one({"id": id}):
        return student


async def get_distinct(mongo: MongoDB = mongodb) -> Union[List[int], None]:
    """
    Get all unique students from the sessions in DB
    :param mongo: MongoDB
    :return: list of student id or None if no sessions in DB
    """
    if students_id := await mongo.session_coll.distinct("recipient"):
        return students_id
