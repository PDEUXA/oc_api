from typing import List

from app.schema.invoice import InvoiceItem


def get_range(r_min, r_max, step=19) -> List[dict]:
    """
    For a list of dict (range_min and range_max) from parameters
    :param r_min: start of range
    :param r_max: end of range
    :param step: size of range
    :return:
    """
    output = []
    complete_range = (r_max - r_min) // step + 1
    for i in range(complete_range):
        output.append({"range_min": i * (step + 1),
                       "range_max": (i + 1) * step + i})
    return output


def define_price(item: InvoiceItem) -> InvoiceItem:
    price_level = {"1": 30, "2": 35, "3": 40}
    item.unit_price = price_level[item.projectLevel]
    if item.student_status != "Financé par un tiers" and item.type == "mentoring":
        item.unit_price /= 2
    if item.status != "completed":
        item.unit_price /= 2
    item.price = item.count * item.unit_price
    return item


def generate_forfait(student_set: set) -> InvoiceItem:
    """
    Create an invoice item corresponding to self-financed student package
    :param student_set: set of unique student
    :return: InvoiceItem
    """
    unique_student = len(list(set(student_set)))
    forfait = InvoiceItem(**{"type": "Forfait inter-sessions", "unit_price": 30})
    forfait.price = unique_student * forfait.unit_price
    forfait.count = unique_student
    return forfait
