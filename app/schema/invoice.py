"""
Schema for invoice
"""
from typing import List, Optional

from pydantic import BaseModel


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


class InvoiceModel(BaseModel):
    date: str
    status: Optional[str] = "Draft"
    id: str
    total: Optional[float] = 0
    item: List[InvoiceItem]
