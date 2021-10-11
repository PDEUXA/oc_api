"""
API routes relating to utilities:

/webhook/session
    POST: post_session_event

"""

from fastapi import HTTPException, APIRouter
from starlette import status

from app.core.db import mongodb
from app.crud.student import find_student_with_email
from app.routes.dependencies import get_me
from app.schema.sessions import SessionOutModel
from app.schema.utils import CalendlyWebHook
from app.services.utils import schedule_session_wrapper

router = APIRouter(prefix="/webhook",
                   tags=["webhook"],
                   responses={404: {"description": "Not found"}})


@router.post("/session",
             response_model=None,
             response_description="Webhook Calendly Session",
             status_code=status.HTTP_200_OK)
async def post_session_event(event: dict) -> SessionOutModel:
    """
    Receive event from webhook, parseIt, then schedule
    \f
    :return: List[UserOutputModel]
    """
    event = CalendlyWebHook(**{"event": event["event"],
                               "time": event["time"],
                               "start": event["payload"]["event"]["start_time"],
                               "name": event["payload"]["invitee"]["name"],
                               "email": event["payload"]["invitee"]["email"]})
    user = await get_me(mongodb.get_token(), cookie="")
    if student := await find_student_with_email(event.email):
        session = await schedule_session_wrapper(student["id"], user, event.start)
        return session
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students")
