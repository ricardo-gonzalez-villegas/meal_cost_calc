from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
import time
import os

load_dotenv(override=True)

USER_AGENT = os.getenv('USER_AGENT')

options = webdriver.ChromeOptions()
# options to stop automatic bot detection while scraping
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
options.add_argument(f"--user-agent={USER_AGENT}")

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


def scrape_product_info_by_upc(upc: int) -> dict:
    driver.get(f"https://www.meijer.com/shopping/search.html?text={upc}")
    time.sleep(2)

    product_info = dict()

    try:
        prod_title = driver.find_element(By.CLASS_NAME, value="product-tile__title")
        product_info = parse_product_info(title=prod_title.text)

        prod_price = driver.find_element(By.CLASS_NAME, value="product-tile__regular-price-text")
        product_info["price"] = prod_price.text.replace('$', '')
    except NoSuchElementException:
        return product_info

    if len(driver.find_elements(By.CLASS_NAME, value="product-tile__sale-price")) > 0:
        prod_sale_price = driver.find_element(By.CLASS_NAME, value="product-tile__sale-price")
        product_info["sale_price"] = prod_sale_price.text.replace('$', '')

    driver.quit()

    return product_info


def parse_product_info(title: str) -> dict:
    if "-" in title:
        info = title.split("-")
        name = info[0].strip()
    else:
        info = title.split(",")
        name = info[0].strip()

    description = info[-1].strip().split(" ")
    qty = description[0].strip()
    units = description[1].strip()

    return {"name": name, "qty": qty, "units": units}