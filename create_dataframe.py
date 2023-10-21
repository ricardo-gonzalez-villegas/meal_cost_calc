import pandas as pd

upc = list()
name = list()
qty = list()
units = list()
price = list()
sale_price = list()


def populate_lists(product_info: dict) -> None:
    if len(product_info) == 0:
        return
    upc.append(product_info["upc"])
    name.append(product_info["name"])
    if "qty" in product_info.keys():
        qty.append(product_info["qty"])
    else:
        qty.append("")
    if "units" in product_info.keys():
        units.append(product_info["units"])
    else:
        units.append("")
    price.append(product_info["price"])
    if "sale_price" in product_info.keys():
        sale_price.append(product_info["sale_price"])
    else:
        sale_price.append("")
