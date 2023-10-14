from selenium import webdriver

options = webdriver.ChromeOptions()
# options to stop automatic bot detection while scraping
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
# options.add_argument("--headless")

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.get("https://meijer.com")

input("Press enter to quit.")

driver.quit()
