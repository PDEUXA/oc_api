from typing import List

from pydantic import BaseModel


class InvoiceItem(BaseModel):
    item_type: str
    projectLevel: str
    status: str


class InvoiceModel(BaseModel):
    date: str
    id: int
    item: List[InvoiceItem]
    publicId: str
