from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status

from crud.invoice import create_invoice, update_full_invoice, delete_invoice, find_invoice_by_id, find_all_invoices, \
    add_invoice
from schema.invoice import InvoiceModel, InvoiceInModel

router = APIRouter(prefix="/invoices",
                   tags=["invoices"],
                   responses={404: {"description": "Not found"}},
                   )


@router.post("/",
             response_model=InvoiceModel,
             response_description="Create an Invoice",
             status_code=status.HTTP_201_CREATED)
async def add_new_invoice(year: str, month: str) -> InvoiceModel:
    invoice = await add_invoice(year + "-" + month)
    if invoice:
        return invoice
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice already exist")


@router.get("/",
            response_model=List[InvoiceModel],
            response_description="Get all invoices",
            status_code=status.HTTP_200_OK)
async def get_all_invoice() -> List[InvoiceModel]:
    invoices = await find_all_invoices()
    if invoices:
        return invoices
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.get("/{id}",
            response_model=InvoiceModel,
            response_description="Get an Invoice",
            status_code=status.HTTP_200_OK)
async def get_invoice(id: str) -> InvoiceModel:
    invoice = await find_invoice_by_id(id)
    if invoice:
        return invoice
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.delete("/{id}",
               # response_model=InvoiceModel,
               response_description="Delete an Invoice",
               status_code=status.HTTP_200_OK)
async def remove_invoice(id: str) -> InvoiceModel:
    invoice = await delete_invoice(id)
    if invoice:
        return "Invoice " + id + " deleted"
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.put("/{id}",
            # response_model=InvoiceModel,
            response_description="Refresh an Invoice with new session",
            status_code=status.HTTP_201_CREATED)
async def refresh_invoice(id: str) -> InvoiceModel:
    invoice = await update_full_invoice(id)
    if invoice:
        return invoice
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
