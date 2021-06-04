from typing import List

from fastapi import APIRouter, status, HTTPException, Body

from core.db import db, post_student
from schema.sessions import SessionModel, SessionOutputModel
from schema.users import UserSimpleModel, UserDetailledModel, UserDetailledModelPlus
from services.oc_api import get_student_type

router = APIRouter(prefix="/student",
                   tags=["student"],
                   responses={404: {"description": "Not found"}})


@router.get("/",
            response_model=List[UserSimpleModel],
            response_description="Get all students",
            status_code=status.HTTP_200_OK)
async def get_students() -> UserSimpleModel:
    cursor = db["usersimples"].find()
    students = []
    for document in await cursor.to_list(length=100):
        students.append(document)
    if students:
        return students
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students")


@router.post("/",
             response_model=UserDetailledModel,
             response_description="Add a student",
             status_code=status.HTTP_201_CREATED)
async def add_new_student(student: UserDetailledModel) -> UserDetailledModel:
    if result := await post_student(student):
        student_type = get_student_type()
        student_plus = UserDetailledModelPlus(**{**student.dict(),
                                                 **{"student_type": student_type}})
        return student
    else:
        print('else')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already exist")


@router.get("/{id}",
            response_model=UserSimpleModel,
            response_description="Get a single student by his id",
            status_code=status.HTTP_200_OK)
async def get_student_by_id(id: int) -> UserSimpleModel:
    if student := await db["usersimples"].find_one({"id": id}):
        return student
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@router.get("/{id}/sessions",
            response_model=List[SessionOutputModel],
            response_description="Return all sessions from a student",
            status_code=status.HTTP_200_OK)
async def get_student_sessions(id: int) -> List[SessionModel]:
    cursor = db["sessions"].find({"recipient.id": id})
    sessions = []
    for document in await cursor.to_list(length=100):
        sessions.append(document)
    if sessions:
        return sessions
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
