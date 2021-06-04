from typing import Union

from pydantic import BaseModel


class UserSimpleModel(BaseModel):
    displayableName: str
    id: int
    profilePicture: str
    publicId: str


class UserDetailledModel(BaseModel):
    displayName: str
    email: str
    enrollment: str
    firstName: str
    id: int
    identityLocked: bool
    language: str
    lastName: str
    openClassroomsProfileUrl: str
    organization: Union[str, None]
    premium: bool
    profilePicture: str


class UserDetailledModelPlus(BaseModel):
    displayName: str
    email: str
    enrollment: str
    firstName: str
    id: int
    identityLocked: bool
    language: str
    lastName: str
    openClassroomsProfileUrl: str
    organization: Union[str, None]
    premium: bool
    profilePicture: str
    student_type: str


class UserSimpleOutput(BaseModel):
    displayableName: str
    id: int
