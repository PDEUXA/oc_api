"""
Schema for session
"""
from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel
from app.schema.users import UserInputModel


class SessionInputModel(BaseModel):
    """

    """
    projectLevel: str
    expert: UserInputModel
    id: int
    recipient: UserInputModel
    sessionDate: datetime
    lifeCycleStatus: str
    status: str
    type: str
    videoConference: Union[None, str]


class SessionScheduleInModel(BaseModel):
    studentId: int
    sessionDate: datetime


class SessionScheduleRequestModel(BaseModel):
    studentId: int
    mentorId: int
    sessionDate: datetime
    isDefense: Optional[bool] = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class SessionOutputModel(BaseModel):
    projectLevel: str
    sessionDate: datetime
    status: str
    type: str
    id: int
    recipient: int


class SessionModel(BaseModel):
    projectLevel: str
    id: int
    recipient: int
    sessionDate: datetime
    lifeCycleStatus: str
    status: str
    type: str
    videoConference: Union[None, str]
