"""
Schema for invoice
"""
from typing import List, Optional

from pydantic import BaseModel
from pydantic.types import Enum


class StatusEnum(str, Enum):
    draft = 'Draft'
    sent = 'Sent'
    payed = 'Payed'


class InvoiceInModel(BaseModel):
    year: str
    month: str


class InvoiceItem(BaseModel):
    type: str
    projectLevel: Optional[str] = ""
    status: Optional[str] = ""
    student_status: Optional[str] = ""
    count: Optional[int] = 0
    unit_price: Optional[float] = 0
    price: Optional[float] = 0


class FileInvoice(BaseModel):
    file: bytes = None
    filename: str = None


class FileInvoiceOut(BaseModel):
    filename: str = None


class InvoiceModel(BaseModel):
    date: str
    status: Optional[StatusEnum] = "Draft"
    id: str
    total: Optional[float] = 0
    item: List[InvoiceItem]
    file: Optional[FileInvoice] = None


class InvoiceOutModel(BaseModel):
    date: str = ""
    status: Optional[StatusEnum] = "Draft"
    id: str = ""
    total: Optional[float] = 0
    item: List[InvoiceItem] = []
    file: Optional[FileInvoiceOut] = None
