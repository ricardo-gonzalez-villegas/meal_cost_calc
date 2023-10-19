from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import time
import os

load_dotenv(override=True)

USER_AGENT = os.getenv('USER_AGENT')
MEIJER_LOGIN = os.getenv('MEIJER_LOGIN')
MEIJER_PASSWORD = os.getenv('MEIJER_PASSWORD')

options = webdriver.ChromeOptions()
# options to stop automatic bot detection while scraping
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
options.add_argument(f"--user-agent={USER_AGENT}")
options.add_argument("--window-size=1920,1080")
options.add_experimental_option("prefs", {
    "download.default_directory": "./receipts",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
})

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


# clicks on receipt and downloads pdf then renames file with date of purchase
async def download_receipt_pdf(receipt, date):
    print("Getting receipt for date: " + date)
    receipt.find_element(By.CLASS_NAME, "order-receipt__show-pdf").click()
    time.sleep(2)
    current_window = driver.current_window_handle
    windows = driver.window_handles

    for window in windows:
        if window != current_window:
            date = date.replace("/", "_")
            driver.switch_to.window(window)
            old_pdf_name = "./receipts/meijer_digital_receipt.pdf"
            new_file_name = f"./receipts/{date}.pdf"
            os.rename(old_pdf_name, new_file_name)
            print("File downloaded...")
            driver.close()
            driver.switch_to.window(current_window)


# logs into meijer account and navigates to receipts page
# goes through every receipt on page until it locates one with a date that is older than starting date
# clicks on receipt and waits until screenshot is taken before continuing down the page
async def download_meijer_receipts(starting_date: str) -> None:
    print("Starting process...")
    start_date = datetime.strptime(starting_date, "%m/%d/%Y")

    driver.get("https://www.meijer.com/")
    time.sleep(2)

    driver.find_element(By.CLASS_NAME, "meijer-header__account-signin-button").click()
    time.sleep(2)

    print("Logging in...")
    driver.find_element(By.XPATH, '//button[text()="Sign In"]').click()
    time.sleep(2)

    driver.find_element(By.ID, "input27").send_keys(MEIJER_LOGIN)
    driver.find_element(By.ID, "input35").send_keys(MEIJER_PASSWORD)
    driver.find_element(By.CLASS_NAME, "button").click()
    time.sleep(2)
    print("Logged in...")

    driver.find_element(By.CLASS_NAME, "meijer-header__account-signin-button").click()
    driver.find_element(By.XPATH, '//a[text()="My Orders & Receipts"]').click()
    time.sleep(2)

    driver.find_element(By.XPATH, '//button[text()="In-Store Receipts"]').click()
    print("Finding receipts...")
    time.sleep(2)

    receipt_list = driver.find_elements(By.CLASS_NAME, "order-receipt__list-tile")

    for receipt in receipt_list:
        info = receipt.find_element(By.CLASS_NAME, "order-receipt__list-receipt-info")
        date_div = info.find_element(By.TAG_NAME, "div").text
        date_field_text = date_div.split(":")
        date = date_field_text[1].strip()

        receipt_date = datetime.strptime(date, "%m/%d/%Y")

        if receipt_date.date() > start_date.date():
            await download_receipt_pdf(receipt, date)

    print("Downloads finished...")
    driver.quit()


asyncio.run(download_meijer_receipts(starting_date="09/01/2023"))
