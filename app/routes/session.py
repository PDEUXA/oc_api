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
from datetime import datetime
from typing import List, Union

import pydantic
from fastapi import APIRouter, status, HTTPException, Depends

from app.core.utils import get_range
from app.crud.session import find_session_by_id, create_session, delete_session, \
    find_sessions_by_date
from app.crud.student import get_distinct, find_student_with_id, create_student
from app.routes.dependencies import get_me
from app.schema.authentification import UserAuth
from app.schema.sessions import SessionModel, SessionScheduleInModel, SessionOutModel
from app.schema.users import UserModel
from app.services.oc_api import update_session_api, get_student_type, delete_session_oc
from app.services.utils import schedule_session_wrapper

router = APIRouter(prefix="/session",
                   tags=["session"],
                   responses={404: {"description": "Not found"}})


@router.get("/{id}",
            response_model=SessionOutModel,
            response_description="Session found",
            status_code=status.HTTP_200_OK)
async def get_session_by_id(id: int) -> SessionOutModel:
    """
     Get the session according to its id:
     - **id**: integer representing the session id.
    \f
     :param id: int
     :return: SessionOutputModel
     """
    session = await find_session_by_id(id=id)
    if session.id:
        return session
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("/",
             response_model=Union[SessionModel, None],
             response_description="Session sceduled with student.",
             status_code=status.HTTP_201_CREATED)
async def schedule_session(schedule: SessionScheduleInModel,
                           user: UserAuth = Depends(get_me)) -> SessionOutModel:
    """
    Schedule a session
    - **schedule** : SessionScheduleInModel
        - **studentId**: integer representing the student id.
        - **sessionDate**: date in ISO format/
    \f
    :param schedule: SessionScheduleInModel
    :param user: request
    :return:
    """
    session = await schedule_session_wrapper(schedule.studentId, user, schedule.sessionDate)
    return session

    # if sessions := await find_session_by_date(date=schedule.sessionDate, duration=60):
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A session exist at the same date")
    #
    # new_session = SessionScheduleRequestModel(**{"studentId": schedule.studentId,
    #                                              "mentorId": user.id,
    #                                              "sessionDate": schedule.sessionDate})
    # session_saved = schedule_meeting(new_session, user.cookie)
    # if session_saved is not None:
    #     if session_saved.status_code != 201:
    #         raise HTTPException(status_code=session_saved.status_code, detail=session_saved.json())
    #     # find session in OC
    #     session = find_specific_session(user.id, user.token, "pending", after=schedule.sessionDate)
    #     if session:
    #         session = session[0]
    #         del session["expert"]
    #         session["recipient"] = session["recipient"]["id"]
    #         if await create_session(SessionModel(**session)):
    #             return session


@router.delete("/{id}",
               response_model=set,
               response_description="Session Deleted",
               status_code=status.HTTP_200_OK)
async def remove_session(id: int,
                         user: UserAuth = Depends(get_me)) -> set:
    """
    Remove session from DB on OC according to its id
    - **id**: integer representing the session id.
    \f
    :param id: int
    :param user:
    :return:
    """
    if session := await delete_session(id):
        delete_session_oc(id, user.cookie)
    else:
        print("session not in db")
        delete_session_oc(id, user.cookie)
    return {"Session " + str(id) + " deleted"}


@router.delete("/",
               response_model=List[SessionOutModel],
               response_description="Sessions Deleted",
               status_code=status.HTTP_200_OK)
async def remove_sessions(sessionDate: datetime,
                          user: UserAuth = Depends(get_me)):
    """
    Remove sessions from DB and OC after requested date:
    - **sessionDate** : date with ISO format
    \f
    :param sessionDate: date in format Y-m-dTHH:MM:SSZ
    :param user: Request
    :return: List[SessionOutModel]
    """
    if sessions := await find_sessions_by_date(sessionDate):
        deleted = []
        for session in sessions:
            if delete_session_oc(session.id, user.cookie):
                await delete_session(session.id)
                deleted.append(session)
        return deleted
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No session found")


@router.put("/update_sessions",
            response_model=List[SessionModel],
            response_description="Sessions fetched",
            status_code=status.HTTP_201_CREATED)
async def fetch_sessions(user: UserAuth = Depends(get_me)) -> List[SessionModel]:
    """
    Fetch session from OC
    \f
    :param user: Request
    :return: List[SessionModel]
    """
    authorization_header = user.token
    sessions, items_range = update_session_api(user_id=user.id,
                                               range_min=0,
                                               range_max=19,
                                               return_range=True,
                                               authorization=authorization_header)
    if not sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue when fetching")
    for range_ in get_range(0, items_range)[1:-1]:
        sessions += update_session_api(user_id=user.id,
                                       range_min=range_["range_min"],
                                       range_max=range_["range_max"],
                                       authorization=authorization_header)
    result = []
    for session in sessions:
        del session["expert"]
        session["recipient"] = session["recipient"]["id"]
        try:
            if await create_session(SessionModel(**session)):
                result.append(SessionModel(**session))
        except pydantic.error_wrappers.ValidationError:
            pass
    if students_id := await get_distinct():
        for student_id in students_id:
            student = await find_student_with_id(student_id)
            if not student.id:
                student = UserModel(**get_student_type(student_id, authorization_header, user.cookie))
                await create_student(student)
    return result
