"""
Schema for utilities
"""
from typing import List

from pydantic import BaseModel


class CalendlyOwner(BaseModel):
    uuid: str
    type: str


class CalendlyEventType(BaseModel):
    uuid: str
    kind: str
    slug: str
    name: str
    duration: int
    owner: CalendlyOwner


class CalendlyEvent(BaseModel):
    uuid: str
    assigned_to: List[str]
    extended_assigned_to: dict
    start_time: str
    start_time_pretty: str
    invitee_start_time: str
    invitee_start_time_pretty: str
    end_time: str
    end_time_pretty: str
    invitee_end_time: str
    invitee_end_time_pretty: str
    created_at: str
    canceled: bool
    canceler_name: str
    cancel_reason: str
    canceled_at: str
    location: str


class CalendlyInvitee(BaseModel):
    uuid: str
    name: str
    email: str
    timezone: str
    create_at: str
    is_reschedule: bool
    payment: List[dict]


class CalendlyPayload(BaseModel):
    event_type: CalendlyEventType
    event: CalendlyEvent
    invitee: CalendlyInvitee


class CalendlyWebHookIn(BaseModel):
    event: str
    time: str
    start: str
    name: str
    email: str


class CalendlyWebHook(BaseModel):
    event: str
    time: str
    start: str
    name: str
    email: str
