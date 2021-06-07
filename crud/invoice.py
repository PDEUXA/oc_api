from core.config import MONGO_STUDENT_COLL
from core.db import MongoDB, mongodb
from core.utils import define_price, generate_forfait
from schema.invoice import InvoiceModel, InvoiceInModel, InvoiceItem


async def find_invoice_by_date(date: str, mongo: MongoDB = mongodb):
    if invoice := await mongo.invoice_coll.find_one({"date": date}):
        return invoice


async def find_invoice_by_id(id: str, mongo: MongoDB = mongodb):
    if invoice := await mongo.invoice_coll.find_one({"id": id}):
        return invoice


async def find_all_invoices(mongo: MongoDB = mongodb):
    cursor = mongo.invoice_coll.find()
    invoices = []
    for document in await cursor.to_list(length=100):
        invoices.append(document)
    if invoices:
        return invoices


async def create_invoice(date: str, mongo: MongoDB = mongodb):
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
                'from': MONGO_STUDENT_COLL,
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

    for r in result:
        if r["student_status"] == "Auto-financé":
            auto_student += [student["displayName"] for student in r["students"]]
        items.append(define_price(InvoiceItem(**r)))

    if auto_student:
        items.append(generate_forfait(auto_student))

    total = sum([item.price for item in items])
    invoice = InvoiceModel(**{"date": date,
                              "id": "OC-" + date,
                              "item": items,
                              "total": total})
    await mongo.invoice_coll.insert_one(invoice.dict())
    return invoice


async def delete_invoice(id: str, mongo: MongoDB = mongodb):
    invoice = await mongo.invoice_coll.delete_one({"id": id})
    return invoice.deleted_count


async def update_full_invoice(id: str):
    if invoice := await find_invoice_by_id(id):
        date = invoice["date"]
        await delete_invoice(id)
        return await create_invoice(date)


async def add_invoice(date: str):
    if invoice := await find_invoice_by_date(date):
        return None
    return await create_invoice(date)
