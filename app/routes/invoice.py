"""
API routes relating to the invoices:
/
    POST: add_new_invoice
    GET: get_all_invoice,

/{id}
    GET -> get_invoice
    DELETE -> remove_invoice
    PUT -> refresh_invoice
"""

from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status

from app.crud.invoice import add_invoice, find_all_invoices, find_invoice_by_id, delete_invoice, update_full_invoice
from app.schema.invoice import InvoiceModel

router = APIRouter(prefix="/invoices",
                   tags=["invoices"],
                   responses={404: {"description": "Not found"}},
                   )


@router.post("/",
             response_model=InvoiceModel,
             response_description="Create an Invoice",
             status_code=status.HTTP_201_CREATED)
async def add_new_invoice(year: str, month: str) -> InvoiceModel:
    """
    Post a new Invoice (created from year and month param)
        HTTP 409 if the invoice exists
    :param year: str
    :param month: str
    :return:
    """
    invoice = await add_invoice(year + "-" + month)
    if invoice:
        return invoice
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice already exist")


@router.get("/",
            response_model=List[InvoiceModel],
            response_description="Get all invoices",
            status_code=status.HTTP_200_OK)
async def get_all_invoice() -> List[InvoiceModel]:
    """
    Get all invoices from DB
        HTTP 404 if there is no invoices
    :return: list of InvoiceModel
    """
    invoices = await find_all_invoices()
    if invoices:
        return invoices
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.get("/{id}",
            response_model=InvoiceModel,
            response_description="Get an Invoice",
            status_code=status.HTTP_200_OK)
async def get_invoice(id: str) -> InvoiceModel:
    """
    Get the invoice according to its id
        HTTP 404 if the invoice does not exist
    :param id: str
    :return: Invoice Model
    """
    invoice = await find_invoice_by_id(id)
    if invoice:
        return invoice
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.delete("/{id}",
               # response_model=InvoiceModel,
               response_description="Delete an Invoice",
               status_code=status.HTTP_200_OK)
async def remove_invoice(id: str) -> InvoiceModel:
    """
    Delete the invoice according to its id
        HTTP 404 if the invoice does not exist
    :param id: str
    :return: InvoiceModel
    """
    invoice = await delete_invoice(id)
    if invoice:
        return "Invoice " + id + " deleted"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.put("/{id}",
            response_model=InvoiceModel,
            response_description="Refresh an Invoice with new session",
            status_code=status.HTTP_201_CREATED)
async def refresh_invoice(id: str) -> InvoiceModel:
    """
    Refresh the invoice with the sessions
        HTTP 404 if the invoice does not exist
    :param id: str
    :return: InvoiceModel
    """
    invoice = await update_full_invoice(id)
    if invoice:
        return invoice
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
