from typing import List

from fastapi import APIRouter, status, HTTPException, Depends

from crud.student import get_all_students, create_student, get_student_with_id, get_student_all_sessions
from routes.dependencies import get_me
from schema.sessions import SessionOutputModel
from schema.users import UserOutputModel, UserModel

router = APIRouter(prefix="/students",
                   tags=["students"],
                   responses={404: {"description": "Not found"}})


@router.get("/",
            response_model=List[UserOutputModel],
            response_description="Get all students",
            status_code=status.HTTP_200_OK)
async def get_students() -> List[UserOutputModel]:
    """
    Get all students from db
    :return: List of student model
    """
    if students := await get_all_students():
        return students
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students")


@router.post("/",
             response_model=UserModel,
             response_description="Add a student",
             status_code=status.HTTP_201_CREATED)
async def add_new_student(student: UserModel) -> UserModel:
    if await create_student(student):
        student = UserModel(**student.dict())
        return student
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already exist")


@router.get("/{id}",
            response_model=UserOutputModel,
            response_description="Get a single student by his id",
            status_code=status.HTTP_200_OK)
async def get_student_by_id(id: int) -> UserOutputModel:
    if student := await get_student_with_id(id=id):
        return student
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@router.get("/{id}/sessions",
            response_model=List[SessionOutputModel],
            response_description="Return all sessions from a student",
            status_code=status.HTTP_200_OK)
async def get_student_sessions(id: int) -> List[SessionOutputModel]:
    sessions = await get_student_all_sessions(id=id)
    if sessions:
        return sessions
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

@router.post("/{id}/schedule",
             response_model=UserModel,
             response_description="Schedule a meeting with the student",
             status_code=status.HTTP_201_CREATED)
async def schedule_meeting_with_student(id:int) -> UserModel:
    pass
