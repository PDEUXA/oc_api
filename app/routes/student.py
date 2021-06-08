"""
API routes relating to the invoices:

/
    POST: add_new_student
    GET: get_all_students,

/update_session
    PUT -> fetch_sessions

/{id}
    GET -> get_student_by_id
/{id}/sessions
    GET -> get_student_sessions
/{id}/schedule
    POST -> schedule
"""
from typing import List

from fastapi import APIRouter, status, HTTPException

from app.crud.student import fetch_all_students, create_student, find_student_with_id, get_student_all_sessions
from app.schema.sessions import SessionOutputModel
from app.schema.users import UserOutputModel, UserModel

router = APIRouter(prefix="/students",
                   tags=["students"],
                   responses={404: {"description": "Not found"}})


@router.get("/",
            response_model=List[UserOutputModel],
            response_description="Get all students",
            status_code=status.HTTP_200_OK)
async def get_all_students() -> List[UserOutputModel]:
    """
    Get all students from db
        HTTP 404 No Students
    :return: List[UserOutputModel]
    """
    if students := await fetch_all_students():
        return students
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students")


@router.post("/",
             response_model=UserModel,
             response_description="Add a student",
             status_code=status.HTTP_201_CREATED)
async def add_new_student(student: UserModel) -> UserModel:
    """
    Post a new student
        HTTP 409 Student already exist
    :param student: UserModel
    :return: UserModel
    """
    if await create_student(student):
        student = UserModel(**student.dict())
        return student
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already exist")


@router.get("/{id}",
            response_model=UserOutputModel,
            response_description="Get a single student by his id",
            status_code=status.HTTP_200_OK)
async def get_student_by_id(id: int) -> UserOutputModel:
    """
    Get the student according to its ID
        HTTP 404 Student not found
    :param id: int
    :return: UserOutputModel
    """
    if student := await find_student_with_id(id=id):
        return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@router.get("/{id}/sessions",
            response_model=List[SessionOutputModel],
            response_description="Return all sessions from a student",
            status_code=status.HTTP_200_OK)
async def get_student_sessions(id: int) -> List[SessionOutputModel]:
    """
    Get all sessions from the student according to its id
        HTTP 404 Student not found
    :param id: int
    :return: List[SessionOutputModel]
    """
    sessions = await get_student_all_sessions(id=id)
    if sessions:
        return sessions
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@router.post("/{id}/schedule",
             response_model=UserModel,
             response_description="Schedule a meeting with the student",
             status_code=status.HTTP_201_CREATED)
async def schedule_meeting_with_student(id: int) -> UserModel:
    pass
