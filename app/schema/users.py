"""
Schema for students/users
"""
from typing import Union

from pydantic import BaseModel


class UserOutputModel(BaseModel):
    displayName: str
    id: int
    email: str
    status: str


class UserInputModel(BaseModel):
    displayableName: str
    id: int
    profilePicture: str
    publicId: str


class UserModel(BaseModel):
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
    status: str
