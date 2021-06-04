import pprint
from typing import List

from fastapi import APIRouter, status, HTTPException

from core.db import db
from schema.sessions import SessionModel, SessionOutputModel

router = APIRouter(prefix="/invoice",
                   tags=["invoice"],
                   responses={404: {"description": "Not found"}})


@router.get("/{id}",
            # response_model=SessionOutputModel,
            response_description="Get a single invoice by his id",
            status_code=status.HTTP_200_OK)
async def get_invoice_by_id(id: int):
    if invoice := await db["invoices"].find_one({"id": id}):
        return invoice
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

@router.post("/",
            response_model=SessionOutputModel,
            response_description="Get a single invoice by his id",
            status_code=status.HTTP_200_OK)
async def get_invoice_by_id(id: int) -> SessionOutputModel:
    if session := await db["invoices"].find_one({"id": id}):
        return session
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
