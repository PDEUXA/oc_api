"""
CRUD operation on DB for invoicing:
- find_invoice_by_date
- find_invoice_by_id
- find_all_invoices
- create_invoice
- delete_invoice
- update_full_invoice
- update_pdf_invoice
- update_status_invoice
- add_invoice
"""
from typing import List

from app.core.config import settings
from app.core.db import mongodb, MongoDB
from app.core.utils import generate_forfait, define_price
from app.schema.invoice import InvoiceItem, FileInvoice, InvoiceOutModel, InvoiceModel


async def find_invoice_by_date(date: str, mongo: MongoDB = mongodb) -> InvoiceOutModel:
    """
    Fetch an invoice from the DB with corresponding date
    :param date:  str
    :param mongo: MongoDB
    :return: If invoice in DB return InvoiceModel else None
    """
    if invoice := await mongo.invoice_coll.find_one({"date": date}):
        return InvoiceOutModel(**invoice)
    else:
        return InvoiceOutModel()


async def find_invoice_by_id(id: str, mongo: MongoDB = mongodb) -> InvoiceModel:
    """
    Fetch an invoice from the DB with corresponding id
    :param id:  str
    :param mongo: MongoDB
    :return: If invoice in DB return InvoiceModel else None
    """
    if invoice := await mongo.invoice_coll.find_one({"id": id}):
        return InvoiceModel(**invoice)
    else:
        return InvoiceModel()


async def find_all_invoices(mongo: MongoDB = mongodb) -> List[InvoiceOutModel]:
    """
    Fetch all invoices from the DB
    :param mongo:
    :return: Return a list of InvoiceModel else None
    """
    cursor = mongo.invoice_coll.find()
    invoices = []
    for document in await cursor.to_list(length=100):
        invoices.append(document)
    if invoices:
        return [InvoiceOutModel(**invoice) for invoice in invoices]
    else:
        return [InvoiceOutModel()]


async def create_invoice(date: str, mongo: MongoDB = mongodb) -> InvoiceOutModel:
    """
    Make an aggregation on sessions to group sessions by date,type, status,...
    then create the corresponding document
    :param date: str
    :param mongo: MongoDB
    :return: InvoiceModel
    """
    cursor = mongo.session_coll.aggregate([
        {
            '$match': {
                '$or': [
                    {
                        'status': {
                            '$eq': 'completed'
                        }
                    }, {
                        'status': {
                            '$eq': 'marked student as absent'
                        }
                    }
                ]
            }
        }, {
            '$set': {
                'yearmonth': {
                    '$dateToString': {
                        'date': '$sessionDate',
                        'format': '%Y-%m'
                    }
                }
            }
        }, {
            '$match': {
                'yearmonth': {
                    '$eq': date
                }
            }
        }, {
            '$lookup': {
                'from': settings.MONGO_STUDENT_COLL,
                'as': 'student',
                'let': {
                    'recipient_id': '$recipient'
                },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$id', '$$recipient_id'
                                ]
                            }
                        }
                    }, {
                        '$project': {
                            'status': 1,
                            'displayName': 1
                        }
                    }
                ]
            }
        }, {
            '$unwind': {
                'path': '$student'
            }
        }, {
            '$group': {
                '_id': {
                    'yearmonth': '$yearmonth',
                    'projectLevel': '$projectLevel',
                    'type': '$type',
                    'status': '$status',
                    'student_status': '$student.status'
                },
                'students': {
                    '$addToSet': '$student'
                },
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$project': {
                'yearmonth': '$_id.yearmonth',
                'projectLevel': '$_id.projectLevel',
                'type': '$_id.type',
                'status': '$_id.status',
                'student_status': '$_id.student_status',
                'count': 1,
                'students': 1
            }
        }, {
            '$sort': {
                'yearmonth': -1
            }
        }
    ])
    result = await cursor.to_list(10)
    items, auto_student = [], []

    for item in result:
        if item["student_status"] == "Auto-financé":
            auto_student += [student["displayName"] for student in item["students"]]
        items.append(define_price(InvoiceItem(**item)))

    if auto_student:
        items.append(generate_forfait(auto_student))

    total = sum([item.price for item in items])
    invoice = InvoiceOutModel(**{"date": date,
                                 "id": "OC-" + date,
                                 "item": items,
                                 "total": total})
    await mongo.invoice_coll.insert_one(invoice.dict())
    return invoice


async def delete_invoice(id: str, mongo: MongoDB = mongodb) -> int:
    """
    Delete an invoice in the DB with the corresponding id
    :param id: str
    :param mongo: MongoDB
    :return: Number of invoice deleted
    """
    invoice = await mongo.invoice_coll.delete_one({"id": id})
    return invoice.deleted_count


async def update_status_invoice(id: str, status: str, mongo: MongoDB = mongodb) -> InvoiceOutModel:
    """
    Update the status of the invoice
    :param id: str
    :param status: str
    :param mongo: MongoDB
    :return: InvoiceModel or None if the invoice is not DB
    """
    if invoice := await find_invoice_by_id(id):
        await mongo.invoice_coll.update_one({"id": invoice.id}, {'$set': {'status': status}})
        invoice.status = status
        return invoice
    else:
        return InvoiceOutModel()


async def update_pdf_invoice(id: str, file: FileInvoice, mongo: MongoDB = mongodb) -> InvoiceModel:
    """
    Update the pdf of the invoice
    :param id: str
    :param file: bytes
    :param mongo: MongoDB
    :return: InvoiceModel or None if the invoice is not DB
    """
    if invoice := await find_invoice_by_id(id):
        await mongo.invoice_coll.update_one({"id": invoice.id}, {'$set': {'file': file.dict()}})
        invoice.file.filename = file.filename
        return invoice
    else:
        return InvoiceModel()


async def update_full_invoice(id: str) -> InvoiceOutModel:
    """
    Update an invoice by deleting it and recreating it from scratch
    :param id: str
    :return: InvoiceModel or None if the invoice is not DB
    """
    if invoice := await find_invoice_by_id(id):
        date = invoice.date
        await delete_invoice(id)
        return await create_invoice(date)
    else:
        return InvoiceOutModel()


async def add_invoice(date: str) -> InvoiceOutModel:
    """
    Create invoice if it not exist in DB
    :param date: str
    :return: InvoiceModel or None if already present in DB
    """
    invoice = await find_invoice_by_date(date)
    if invoice.id:
        return invoice
    return await create_invoice(date)
