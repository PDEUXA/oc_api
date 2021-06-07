from schema.invoice import InvoiceItem


def get_range(r_min, r_max, step=19):
    output = []
    complete_range = (r_max - r_min) // step + 1
    for i in range(complete_range):
        output.append({"range_min": i * (step + 1),
                       "range_max": (i + 1) * step + i})
    # if (r_max - r_min) % step != 0:
    #     output.append({"range_min": complete_range * (step + 1),
    #                    "range_max": r_max - 1})
    return output


def define_price(item: InvoiceItem):
    price_level = {"1": 30, "2": 35, "3": 40}
    item.unit_price = price_level[item.projectLevel]
    if item.student_status != "Financé par un tiers" and item.type == "mentoring":
        item.unit_price /= 2
    if item.status != "completed":
        item.unit_price /= 2
    item.price = item.count * item.unit_price
    return item


def generate_forfait(student_set):
    unique_student = len(list(set(student_set)))
    forfait = InvoiceItem(**{"type": "Forfait inter-sessions", "unit_price": 30})
    forfait.price = unique_student * forfait.unit_price
    forfait.count = unique_student
    return forfait
