from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
import time
import os
import re

load_dotenv(override=True)

USER_AGENT = os.getenv('USER_AGENT')

options = webdriver.ChromeOptions()
# options to stop automatic bot detection while scraping
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
options.add_argument(f"--user-agent={USER_AGENT}")


# searches for product by UPC code and returns a dict of upc, product name, qty, units and price information
# also returns sale price if product is currently on sale
# returns empty dict if nothing is found
def scrape_product_info_by_upc(upc: str) -> dict:
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(f"https://www.meijer.com/shopping/search.html?text={upc}")
    time.sleep(2)

    product_info = dict()

    try:
        prod_title = driver.find_element(By.CLASS_NAME, value="product-tile__title")
        print(upc)
        product_info = parse_product_info(title=prod_title.text, upc=upc)

        prod_price = driver.find_element(By.CLASS_NAME, value="product-tile__regular-price-text")
        product_info["price"] = prod_price.text.replace('$', '')

    except NoSuchElementException:
        return product_info

    if len(driver.find_elements(By.CLASS_NAME, value="product-tile__sale-price")) > 0:
        prod_sale_price = driver.find_element(By.CLASS_NAME, value="product-tile__sale-price")
        product_info["sale_price"] = prod_sale_price.text.replace('$', '')

    driver.quit()

    return {f"{upc}": product_info}


def parse_product_info(title: str, upc: str) -> dict:
    if "-" in title:
        info = title.split("-")
        name = info[0].strip()
    elif "," in title:
        info = title.split(",")
        name = info[0].strip()
    else:
        if "\n" in title:
            name = title.split("\n")
            name = name[0]
        else:
            name = title.strip()
        return {"name": name}

    # returns only produce name
    if len(upc) <= 4:
        return {"name": name}

    # if there is a space in description string splits it and returns first part of string
    # ex: 5pk 20oz will return 5 pk
    if " " in info[-1].strip():
        description = info[-1].strip().split(" ")

        if re.search("[A-z]+", description[0]):
            qty = re.findall("\\d+", description[0])
            units = re.findall("[A-z]+", description[0])
            return {"name": name, "qty": qty[0], "units": units[0]}
        else:
            qty = description[0].strip()
            units = description[1].strip().replace(".", "")
            return {"name": name, "qty": qty, "units": units}
    else:
        description = info[-1].strip()
        qty = re.findall("\\d+", description)
        units = re.findall("[A-z]+", description)
        return {"name": name, "qty": qty[0], "units": units[0]}
