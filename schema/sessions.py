from datetime import datetime
from typing import Union

from pydantic import BaseModel
from schema.users import UserInputModel, UserOutputModel, UserModel


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


class SessionScheduleModel(BaseModel):
    id: int
    day: int
    month: int
    year: int
    hour: int
    minute: int
    csrf_token: str


class SessionOutputModel(BaseModel):
    projectLevel: str
    sessionDate: datetime
    status: str
    type: str
    id: int
    recipient: int


class SessionModel(BaseModel):
    """

    """
    projectLevel: str
    id: int
    recipient: int
    sessionDate: datetime
    lifeCycleStatus: str
    status: str
    type: str
    videoConference: Union[None, str]
