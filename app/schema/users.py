"""
Schema for students/users
"""
from typing import Union, Optional

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
    enrollment: Optional[str] = ""
    firstName: str
    id: int
    identityLocked: Optional[bool] = False
    language: Optional[str]
    lastName: str
    openClassroomsProfileUrl: Optional[str] = ""
    organization: Optional[Union[str, None]] = ""
    premium: Optional[bool] = False
    profilePicture: Optional[str] = ""
    status: str
