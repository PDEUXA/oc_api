from typing import List

from fastapi import APIRouter, status, HTTPException, Depends, Request

from core.utils import get_range
from crud.session import find_session_by_id, create_session
from crud.student import get_distinct, create_student, get_student_with_id
from routes.dependencies import get_me
from schema.authentification import UserAuth
from schema.sessions import SessionOutputModel, SessionModel, SessionScheduleModel
from schema.users import UserModel
from services.oc_api import update_session_api, get_student_type

router = APIRouter(prefix="/session",
                   tags=["session"],
                   responses={404: {"description": "Not found"}})


@router.get("/{id}",
            response_model=SessionOutputModel,
            response_description="Get a single session by his id",
            status_code=status.HTTP_200_OK)
async def get_session_by_id(id: int) -> SessionOutputModel:
    if session := await find_session_by_id(id=id):
        return session
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("/",
             response_model=SessionScheduleModel,
             response_description="Scehdule a session with a specified student",
             status_code=status.HTTP_201_CREATED)
async def schedule_session(schedule: SessionScheduleModel,
                           user: UserAuth = Depends(get_me)) -> SessionOutputModel:
    pass


# for request with csrf token
#

@router.put("/update_sessions",
            response_model=List[SessionModel],
            response_description="Add sessions",
            status_code=status.HTTP_201_CREATED)
async def fetch_sessions(request: Request, user: UserAuth = Depends(get_me)) -> List[SessionModel]:
    authorization_header = request.headers['Authorization']
    sessions, items_range = update_session_api(user_id=user.id,
                                               range_min=0,
                                               range_max=19,
                                               return_range=True,
                                               authorization=authorization_header)
    if not sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue when fetching")
    for r in get_range(0, items_range)[1:]:
        sessions += update_session_api(user_id=user.id,
                                       range_min=r["range_min"],
                                       range_max=r["range_max"],
                                       authorization=authorization_header)
    result = []
    for session in sessions:
        del session["expert"]
        session["recipient"] = session["recipient"]["id"]
        if await create_session(SessionModel(**session)):
            result.append(SessionModel(**session))
    if students_id := await get_distinct():
        for student_id in students_id:
            if not await get_student_with_id(student_id):
                print(user.cookie)
                student = UserModel(**get_student_type(student_id, authorization_header, user.cookie))
                await create_student(student)
    return result
