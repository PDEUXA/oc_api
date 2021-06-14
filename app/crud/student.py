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


async def create_student(student: UserModel, mongo: MongoDB = mongodb) -> Union[UserModel, None]:
    """

    :param mongo:
    :param student: Student UserModel
    :return: UserModel
    """
    if not await mongo.student_coll.find_one({"id": student.id}):
        await mongo.student_coll.insert_one(student.dict())
        return student


async def get_student_all_sessions(id: int, include_status: str = "", exclude_status: str = "",
                                   mongo: MongoDB = mongodb) -> Union[List[SessionOutputModel], None]:
    """
    Get all sessions from an student from DB
    :param exclude_status: List[str], session status
    :param include_status: List[str], session status
    :param mongo: MongoDB
    :param id: id of the student (int)
    :return: List of SessionOutputModel or None if student has no session
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
        sessions.append(SessionOutputModel(**document))
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
        students.append(UserOutputModel(**document))
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
        return UserOutputModel(**student)


async def get_distinct(mongo: MongoDB = mongodb) -> Union[List[int], None]:
    """
    Get all unique students from the sessions in DB
    :param mongo: MongoDB
    :return: list of student id or None if no sessions in DB
    """
    if students_id := await mongo.session_coll.distinct("recipient"):
        return students_id


async def delete_student(id: int, mongo: MongoDB = mongodb) -> Union[int, None]:
    """
    Delete a student in the DB with the corresponding id
    :param id: str
    :param mongo: MongoDB
    :return: Number of session deleted
    """
    session = await mongo.student_coll.delete_one({"id": id})
    return session.deleted_count
