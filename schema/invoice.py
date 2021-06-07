from typing import List, Optional

from pydantic import BaseModel, validator


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


    # @validator("type")
    # def map_type(cls, v):
    #     mapping = {"mentoring": "Session Mentorat",
    #                "presentation": "Soutenance",
    #                "Forfait inter-sessions": "Forfait inter-sessions"}
    #     return mapping[v]
    #
    # @validator("status")
    # def map_status(cls, v):
    #     mapping = {"completed": "Effectuée",
    #                "marked student as absent": "Etudiant Absent"}
    #     return mapping[v]
    #
    # @validator("student_status")
    # def map_student_status(cls, v):
    #     mapping = {"Auto": "Auto-financé",
    #                "Ext": "Financement externe"}
    #     return mapping[v]


class InvoiceModel(BaseModel):
    date: str
    status: Optional[str] = "Draft"
    id: str
    total: Optional[float] = 0
    item: List[InvoiceItem]
