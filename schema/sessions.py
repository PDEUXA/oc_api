from typing import Union

from pydantic import BaseModel
from schema.users import UserSimpleModel, UserSimpleOutput


class SessionModel(BaseModel):
    """

    """
    projectLevel: str
    expert: UserSimpleModel
    id: int
    recipient: UserSimpleModel
    sessionDate: str
    lifeCycleStatus: str
    status: str
    type: str
    videoConference: Union[None, str]


class SessionOutputModel(BaseModel):
    projectLevel: str
    sessionDate: str
    status: str
    type: str
    id: int
    recipient: UserSimpleOutput
