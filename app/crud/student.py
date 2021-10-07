"""
CRUD operation on DB for interacting with sessions:
- get_student_all_sessions
- create_student
- fetch_all_students
- find_student_with_id
- find_student_with_email
- get_distinct
"""

from typing import List

from app.core.db import mongodb, MongoDB
from app.schema.sessions import SessionOutModel
from app.schema.users import UserModel, UserOutModel


async def create_student(student: UserModel, mongo: MongoDB = mongodb) -> UserModel:
    """

    :param mongo:
    :param student: Student UserModel
    :return: UserModel
    """
    if not await mongo.student_coll.find_one({"id": student.id}):
        await mongo.student_coll.insert_one(student.dict())
        return student
    else:
        return UserModel()


async def get_student_all_sessions(id: int, include_status: str = "", exclude_status: str = "",
                                   mongo: MongoDB = mongodb) -> List[SessionOutModel]:
    """
    Get all sessions from an student from DB
    :param exclude_status: List[str], session status
    :param include_status: List[str], session status
    :param mongo: MongoDB
    :param id: id of the student (int)
    :return: List of SessionOutputModel
    """
    exclude_status = exclude_status.split(",")
    if include_status:
        include_status = include_status.split(",")
        cursor = mongo.session_coll.find(
            {"recipient": id,
             '$and': [
                 {"status": {'$in': include_status}},
                 {"status": {'$nin': exclude_status}}]})
    else:
        cursor = mongo.session_coll.find({"recipient": id, "status": {'$nin': exclude_status}})
    sessions = []
    for document in await cursor.to_list(length=100):
        sessions.append(SessionOutModel(**document))
    if sessions:
        return sessions
    else:
        return [SessionOutModel(**session) for session in sessions]


async def fetch_all_students(mongo: MongoDB = mongodb) -> List[UserOutModel]:
    """
    Fetch all students from DB
    :param mongo: MongoDB
    :return: list of UserOutputModel
    """
    cursor = mongo.student_coll.find()
    students = []
    for document in await cursor.to_list(length=100):
        students.append(UserOutModel(**document))
    if students:
        return students
    else:
        return [UserOutModel(**student) for student in students]


async def find_student_with_email(email: str, mongo: MongoDB = mongodb) -> UserOutModel:
    """
    Fetch a student by its email
    :param email: str
    :param mongo: MongoDB
    :return: UserOutputModel
    """
    if student := await mongo.student_coll.find_one({"email": email}):
        return UserOutModel(**student)
    else:
        return UserOutModel()


async def find_student_with_id(id: int, mongo: MongoDB = mongodb) -> UserOutModel:
    """
    Fetch a student from DB according to its id
    :param id: int
    :param mongo: MongoDB
    :return: UserOutputModel
    """
    if student := await mongo.student_coll.find_one({"id": id}):
        return UserOutModel(**student)
    else:
        return UserOutModel()


async def get_distinct(mongo: MongoDB = mongodb) -> List[int]:
    """
    Get all unique students from the sessions in DB
    :param mongo: MongoDB
    :return: list of student id
    """
    if students_id := await mongo.session_coll.distinct("recipient"):
        return students_id
    else:
        return []


async def delete_student(id: int, mongo: MongoDB = mongodb) -> int:
    """
    Delete a student in the DB with the corresponding id
    :param id: str
    :param mongo: MongoDB
    :return: Number of session deleted
    """
    session = await mongo.student_coll.delete_one({"id": id})
    return session.deleted_count
