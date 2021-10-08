from datetime import datetime

from fastapi import HTTPException
from starlette import status

from app.crud.session import find_session_by_date, create_session
from app.schema.sessions import SessionScheduleRequestModel, SessionModel
from app.services.oc_api import schedule_meeting, find_specific_session


async def schedule_session_wrapper(studentId, user, eventStart):
    # Check if session at the same date exist
    new_session = SessionScheduleRequestModel(**{"studentId": studentId,
                                                 "mentorId": user.id,
                                                 "sessionDate": eventStart.isoformat()})
    if sessions := await find_session_by_date(date=new_session.sessionDate, duration=60):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A session exist at the same date")

    session_oc = schedule_meeting(new_session, user.cookie)
    if session_oc is not None:
        if session_oc.status_code != 201:
            raise HTTPException(status_code=session_oc.status_code, detail=session_oc.text)
        # find session in OC
        session = find_specific_session(user.id, user.token, "pending", after=new_session.sessionDate)
        if session:
            session = session[0]
            del session["expert"]
            session["recipient"] = session["recipient"]["id"]
            if await create_session(SessionModel(**session)):
                return session
        raise HTTPException(status_code=session_oc.status_code, detail="Session not in OC")
