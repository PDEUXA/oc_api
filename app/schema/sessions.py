"""
Schema for session
"""
from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel
from app.schema.users import UserInModel


class SessionScheduleInModel(BaseModel):
    studentId: int
    sessionDate: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class SessionScheduleRequestModel(BaseModel):
    studentId: int
    mentorId: int
    sessionDate: datetime
    isDefense: Optional[bool] = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class SessionOutModel(BaseModel):
    projectLevel: str = ""
    sessionDate: datetime = ""
    status: str = ""
    type: str = ""
    id: int = None
    recipient: int = ""

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class SessionInputModel(SessionOutModel):
    """

    """
    expert: UserInModel
    lifeCycleStatus: str
    videoConference: Union[None, str]


class SessionModel(SessionOutModel):
    lifeCycleStatus: str = ""
    videoConference: Union[None, str] = ""
