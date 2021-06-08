"""
API routes relating to the invoices:
/
    POST: schedule_session
    GET: get_all_invoice,

/update_session
    PUT -> fetch_sessions

/{id}
    GET -> get_session_by_id
    DELETE -> remove_invoice
    PUT -> refresh_invoice
"""
from typing import List

from fastapi import APIRouter, status, HTTPException, Depends, Request

from app.core.utils import get_range
from app.crud.session import find_session_by_id, create_session
from app.crud.student import get_distinct, find_student_with_id, create_student
from app.routes.dependencies import get_me
from app.schema.authentification import UserAuth
from app.schema.sessions import SessionOutputModel, SessionScheduleModel, SessionModel
from app.schema.users import UserModel
from app.services.oc_api import update_session_api, get_student_type

router = APIRouter(prefix="/session",
                   tags=["session"],
                   responses={404: {"description": "Not found"}})


@router.get("/{id}",
            response_model=SessionOutputModel,
            response_description="Get a single session by his id",
            status_code=status.HTTP_200_OK)
async def get_session_by_id(id: int) -> SessionOutputModel:
    """
     Get the session according to its id
         HTTP 404 if the invoice does not exist
     :param id: int
     :return: SessionOutputModel
     """
    if session := await find_session_by_id(id=id):
        return session
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
    """
    Fetch session from OC
        HTTP 404 issue when fetching

    :param request: UserAuth
    :param user: Request
    :return: List[SessionModel]
    """
    authorization_header = request.headers['Authorization']
    sessions, items_range = update_session_api(user_id=user.id,
                                               range_min=0,
                                               range_max=19,
                                               return_range=True,
                                               authorization=authorization_header)
    if not sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue when fetching")
    for range_ in get_range(0, items_range)[1:]:
        sessions += update_session_api(user_id=user.id,
                                       range_min=range_["range_min"],
                                       range_max=range_["range_max"],
                                       authorization=authorization_header)
    result = []
    for session in sessions:
        del session["expert"]
        session["recipient"] = session["recipient"]["id"]
        if await create_session(SessionModel(**session)):
            result.append(SessionModel(**session))
    if students_id := await get_distinct():
        for student_id in students_id:
            if not await find_student_with_id(student_id):
                print(user.cookie)
                student = UserModel(**get_student_type(student_id, authorization_header, user.cookie))
                await create_student(student)
    return result
