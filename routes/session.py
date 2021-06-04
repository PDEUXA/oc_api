import pprint
from typing import List

from fastapi import APIRouter, status, HTTPException

from core.db import db, post_student
from schema.sessions import SessionModel, SessionOutputModel
from schema.users import UserDetailledModel

router = APIRouter(prefix="/session",
                   tags=["session"],
                   responses={404: {"description": "Not found"}})


@router.get("/{id}",
            response_model=SessionOutputModel,
            response_description="Get a single session by his id",
            status_code=status.HTTP_200_OK)
async def get_session_by_id(id: int) -> SessionOutputModel:
    if session := await db["sessions"].find_one({"id": id}):
        return session
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("/batch",
             response_model=SessionModel,
             response_description="Add a student",
             status_code=status.HTTP_201_CREATED)
async def add_sessions(student: SessionModel) -> UserDetailledModel:
    if result := await post_student(student):
        return student
    else:
        print('else')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already exist")



@router.get("/projectLevel/{level}",
            response_model=List[SessionOutputModel],
            response_description="Get all sessions by level",
            status_code=status.HTTP_200_OK)
async def get_sessions_by_level(level: str) -> SessionOutputModel:
    cursor = db["sessions"].find({"projectLevel": level})
    sessions = []
    for document in await cursor.to_list(length=100):
        sessions.append(document)
    if sessions:
        return sessions
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
