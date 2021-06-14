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
from datetime import datetime
from typing import List

from fastapi import APIRouter, status, HTTPException, Depends

from app.crud.session import find_session_by_date, create_session
from app.crud.student import fetch_all_students, create_student, find_student_with_id, get_student_all_sessions
from app.routes.dependencies import get_me
from app.schema.authentification import UserAuth
from app.schema.sessions import SessionOutputModel, SessionScheduleInModel, SessionScheduleRequestModel, SessionModel
from app.schema.users import UserOutputModel, UserModel
from app.services.oc_api import schedule_meeting, find_specific_session

router = APIRouter(prefix="/students",
                   tags=["students"],
                   responses={404: {"description": "Not found"}})


@router.get("/",
            response_model=List[UserOutputModel],
            response_description="Students list",
            status_code=status.HTTP_200_OK)
async def get_all_students() -> List[UserOutputModel]:
    """
    Get all students from db
    \f
    :return: List[UserOutputModel]
    """
    if students := await fetch_all_students():
        return students
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students")


@router.post("/",
             response_model=UserModel,
             response_description="Student added",
             status_code=status.HTTP_201_CREATED)
async def add_new_student(student: UserModel) -> UserModel:
    """
    Add a new student
    - **student**: UserModel
        - **displayName**: string
        - **email**: string
        - **enrollment**: string
        - **firstName**: string
        - **id**: integer
        - **identityLocked**: boolean
        - **language**: string
        - **lastName**: string
        - **openClassroomsProfileUrl**: string
        - **organization**: Union[str, None]
        - **premium**: boolean
        - **profilePicture**: string
        - **status**: string
    \f
    :param student: UserModel
    :return: UserModel
    """
    if await create_student(student):
        student = UserModel(**student.dict())
        return student
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already exist")


@router.get("/{id}",
            response_model=UserOutputModel,
            response_description="Student found",
            status_code=status.HTTP_200_OK)
async def get_student_by_id(id: int) -> UserOutputModel:
    """
    Get the student according to its ID
    - **id** : integer representing the student id.
    \f
    :param id: int
    :return: UserOutputModel
    """
    if student := await find_student_with_id(id=id):
        return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@router.get("/{id}/sessions",
            response_model=List[SessionOutputModel],
            response_description="Session List from student",
            status_code=status.HTTP_200_OK)
async def get_student_sessions(id: int, include_status: str = "", exclude_status: str = "") -> List[SessionOutputModel]:
    """
    Get all sessions from the student according to its id:
    - **id** : integer representing the student id.
    - **include_status** : filter by status (session)
    - **exclude_status**: status to be excluded
    \f
    :param exclude_status: str
    :param include_status: str
    :param id: int
    :return: List[SessionOutputModel]
    """
    sessions = await get_student_all_sessions(id=id, include_status=include_status, exclude_status=exclude_status)
    if sessions:
        return sessions
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessions not found")


@router.post("/{id}/schedule",
             response_model=UserModel,
             response_description="Schedule a meeting with the student",
             status_code=status.HTTP_201_CREATED)
async def schedule_meeting_with_student(id: int, sessionDate: datetime, user: UserAuth = Depends(get_me)) -> UserModel:
    """
    Schedule a session with the student
    - **id** : integer representing the student id.
    - **sessionDate** : date in ISO format.
    \f
    :param id: integer
    :param sessionDate: date
    :param user: request
    :return:
    """
    # Check if session at the same date exist
    schedule = SessionScheduleInModel(**{"sessionDate": sessionDate, "studentId": id})
    if sessions := await find_session_by_date(date=schedule.sessionDate, duration=60):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A session exist at the same date")

    new_session = SessionScheduleRequestModel(**{"studentId": schedule.studentId,
                                                 "mentorId": user.id,
                                                 "sessionDate": schedule.sessionDate})
    session_saved = schedule_meeting(new_session, user.cookie)
    if session_saved is not None:
        if session_saved.status_code != 201:
            raise HTTPException(status_code=session_saved.status_code, detail=session_saved.json())
        # find session in OC
        session = find_specific_session(user.id, user.token, "pending", after=schedule.sessionDate)
        if session:
            session = session[0]
            del session["expert"]
            session["recipient"] = session["recipient"]["id"]
            if await create_session(SessionModel(**session)):
                return session
