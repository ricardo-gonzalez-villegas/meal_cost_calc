import PyPDF2
import os
import re


# gets only text that is located after Grocery section and before mPerks section on receipt
# uses regex and gets all text that is 4 digits or more which are the upc
def filter_product_upc(receipt: str) -> list:
    products = receipt.partition("GROCERY")[2].partition("mPerks")[0]
    upc = re.findall("(\\d{4,})", products)
    return upc


# gets all receipts in folder and reads each one then
# returns a set of product codes from grocery section of each receipt
def parse_pdf_receipts() -> set:
    receipts = os.listdir("receipts")
    upc_set = set()

    for receipt in receipts:
        if receipt == ".DS_Store":
            continue

        file = open(f'receipts/{receipt}', 'rb')
        reader = PyPDF2.PdfReader(file)
        obj = reader.pages[0]
        receipt_text = obj.extract_text()
        upc = filter_product_upc(receipt=receipt_text)
        upc_set.update(upc)
        file.close()

    return upc_set
