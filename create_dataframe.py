from populate_lists import populate_lists
from datetime import date
import pandas as pd

lists = populate_lists()
today = date.today().strftime("%m/%d/%y")

df = pd.DataFrame(lists, columns=['UPC', 'Name', 'Qty', 'Units', 'Price', 'Sale_Price'])

df.to_csv('./product_info.excel.csv', index=False)

print("Finished")
