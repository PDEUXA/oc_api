"""
API routes relating to the invoices:
/
    POST: add_new_invoice
    GET: get_all_invoice

/batch
    POST: create_batch_invoice

/{id}
    GET -> get_invoice
    GET -> get_html_invoice
    GET -> get_pdf_invoice
    DELETE -> remove_invoice
    POST -> create_pdf_invoice
    PUT -> refresh_invoice
    PUT -> change_status_invoice
    PUT -> upload_pdf_invoice
"""
import io
from datetime import datetime
from typing import List

import pdfkit
from fastapi import APIRouter, HTTPException, UploadFile, File
from starlette import status
from starlette.requests import Request
from starlette.responses import StreamingResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from app.crud.invoice import add_invoice, find_all_invoices, find_invoice_by_id, delete_invoice, update_full_invoice, \
    update_status_invoice, update_pdf_invoice
from app.schema.invoice import StatusEnum, FileInvoice, InvoiceOutModel

router = APIRouter(prefix="/invoices",
                   tags=["invoices"],
                   responses={404: {"description": "Not found"}},
                   )
templates = Jinja2Templates(directory="app/templates")


@router.post("/",
             response_model=InvoiceOutModel,
             response_description="Invoice Created",
             status_code=status.HTTP_201_CREATED)
async def add_new_invoice(year: str, month: str) -> InvoiceOutModel:
    """
    Post a new Invoice (created from year and month param)
    - **year**: string representing the year in format YYYY
    - **month** : string representing the month in format MM
    \f
    :param year: str
    :param month: str
    :return:
    """
    invoice = await add_invoice(year + "-" + month)
    if invoice.id:
        return invoice
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice already exist")


@router.post("/batch",
             response_model=List[InvoiceOutModel],
             response_description="Invoice Created",
             status_code=status.HTTP_201_CREATED)
async def create_batch_invoices() -> List[InvoiceOutModel]:
    """
    Post a new Invoice (created from year and month param)
    \f
    :return:
    """
    invoices = []
    for i in range(1, 13):
        if i < 10:
            month = "0" + str(i)
        else:
            month = str(i)
        invoice = await add_invoice("2021" + "-" + month)
        if invoice:
            invoices.append(invoice)
    if invoices[0].id:
        return invoices
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice already exist")


@router.get("/",
            response_model=List[InvoiceOutModel],
            response_description="Invoices list",
            status_code=status.HTTP_200_OK)
async def get_all_invoice() -> List[InvoiceOutModel]:
    """
    Get all invoices from DB
    \f
    :return: list of InvoiceModel
    """
    invoices = await find_all_invoices()
    if invoices[0].id:
        return invoices
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.get("/{id}",
            response_model=InvoiceOutModel,
            response_description="Invoice found",
            status_code=status.HTTP_200_OK)
async def get_invoice(id: str) -> InvoiceOutModel:
    """
    Get the invoice according to its id:
    - **id**: string representing the invoice id.
    \f
    :param id: str
    :return: Invoice Model
    """
    invoice = await find_invoice_by_id(id)
    if invoice.id:
        return invoice
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.delete("/{id}",
               response_description="Invoice Deleted",
               status_code=status.HTTP_200_OK)
async def remove_invoice(id: str) -> str:
    """
    Delete the invoice according to its id
    - **id**: string representing the invoice id.
    \f
    :param id: str
    :return: InvoiceModel
    """
    invoice = await delete_invoice(id)
    if invoice.id:
        return "Invoice " + id + " deleted"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.put("/{id}",
            response_model=InvoiceOutModel,
            response_description="Refreshed invoice",
            status_code=status.HTTP_201_CREATED)
async def refresh_invoice(id: str) -> InvoiceOutModel:
    """
    Refresh the invoice with the sessions
    - **id**: string representing the invoice id.
    \f
    :param id: str
    :return: InvoiceModel
    """
    invoice = await update_full_invoice(id)
    if invoice.id:
        return invoice
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.put("/{id}/status",
            response_model=InvoiceOutModel,
            response_description="Status changed",
            status_code=status.HTTP_201_CREATED)
async def change_status_invoice(id: str, status: StatusEnum) -> InvoiceOutModel:
    """
    Refresh the invoice with the sessions
    - **id**: string representing the invoice id.
    - **status**: string of the new status to be updated
    \f
    :param id: str
    :param status: str
    :return: InvoiceModel
    """
    invoice = await update_status_invoice(id, status)
    if invoice.id:
        return invoice
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.put("/{id}/pdf",
            response_model=InvoiceOutModel,
            response_description="PDF added",
            status_code=status.HTTP_201_CREATED)
async def upload_pdf_invoice(id: str, pdf: UploadFile = File(...)) -> InvoiceOutModel:
    """
    Add a pdf to the invoice
    - **id**: string representing the invoice id.
    - **file**: file-like
    \f
    :param id: str
    :param pdf: bytes
    :return: str
    """
    file_content = await pdf.read()
    await pdf.close()
    invoice = await update_pdf_invoice(id, FileInvoice(**{"filename": pdf.filename, "file": file_content}))
    if invoice.id:
        return invoice
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.get("/{id}/pdf",
            response_model=InvoiceOutModel,
            response_description="PDF fetched",
            status_code=status.HTTP_201_CREATED)
async def get_pdf_invoice(id: str) -> StreamingResponse:
    """
    Get a pdf from the invoice
    - **id**: string representing the invoice id.
    \f
    :return: bytes
    """
    invoice = await find_invoice_by_id(id)
    if invoice.id:
        file = io.BytesIO(invoice.file.file)
        file.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="{}"'.format(invoice.file.filename)
        }
        return StreamingResponse(file, headers=headers)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.get("/{id}/html")
async def get_html_invoice(id: str, request: Request) -> HTMLResponse:
    """
    Get html format of the invoice
    - **id**: string representing the invoice id.
    \f
    :return: HTMLResponse
    """
    invoice = await find_invoice_by_id(id)
    if invoice.id:
        return HTMLResponse(templates.TemplateResponse("invoice.html",
                                                       {"request": request, "invoice": invoice.dict(),
                                                        "date": datetime.today().date().strftime('%d/%m/%Y')}).body)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")


@router.put("/{id}/html/pdf")
async def create_pdf_invoice(id: str, request: Request) -> StreamingResponse:
    """
    Get pdf format of the invoice from html
    - **id**: string representing the invoice id.
    \f
    :return: Filereponse
    """
    invoice = await find_invoice_by_id(id)
    if invoice.id:
        html = templates.TemplateResponse("invoice.html",
                                          {"request": request, "invoice": InvoiceOutModel(**invoice).dict(),
                                           "date": datetime.today().date().strftime('%d/%m/%Y')}).body

        file_b = pdfkit.from_string(html.decode("utf8"), output_path=False)
        file = io.BytesIO(file_b)
        file.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="{}.pdf"'.format(invoice["id"])
        }
        await update_pdf_invoice(id, FileInvoice(**{"filename": invoice["id"] + ".pdf", "file": file_b}))
        return StreamingResponse(file, headers=headers)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
