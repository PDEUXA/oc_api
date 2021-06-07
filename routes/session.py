import pprint
from typing import List

from fastapi import APIRouter, status, HTTPException, Depends, Request

from core.db import db, post_student, post_session
from routes.dependencies import get_me
from schema.sessions import SessionModel, SessionOutputModel
from schema.users import UserDetailledModel
from services.oc_api import update_session_api, get_range

router = APIRouter(prefix="/session",
                   tags=["session"],
                   responses={404: {"description": "Not found"}}, dependencies=[Depends(get_me)])


@router.get("/{id}",
            response_model=SessionOutputModel,
            response_description="Get a single session by his id",
            status_code=status.HTTP_200_OK)
async def get_session_by_id(id: int) -> SessionOutputModel:
    if session := await db["sessions"].find_one({"id": id}):
        return session
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("/update_sessions",
             response_model=List[SessionModel],
             response_description="Add sessions",
             status_code=status.HTTP_201_CREATED)
async def fetch_sessions(request: Request) -> List[SessionModel]:
    sessions, items_range = update_session_api(0, 19, return_range=True,
                                               authorization=request.headers['Authorization'][7:])
    for r in get_range(0, items_range)[1:]:
        sessions += update_session_api(*r,authorization=request.headers['Authorization'][7:])
    result = []
    for session in sessions:
        if await post_session(SessionModel(**session)):
            result.append(SessionModel(**session))
    return result

    # sessions, items_range = update_session_api(0, 19, return_range=True, token=request.headers['Authorization'])
    # print(items_range)
    # if result := await post_student(student):
    #     return student
    # else:
    #     print('else')
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already exist")


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
