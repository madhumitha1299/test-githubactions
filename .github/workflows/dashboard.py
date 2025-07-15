import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def configure_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def test_page_access(driver, wait):
    try:
        # Try to directly access the Reports page (may redirect to SSO)
        driver.get("https://workflow.cable.comcast.com/reporting")

        # Wait for the body or any known element to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("✅ Page loaded successfully!")

        # Print page title and sample content
        print("Page Title:", driver.title)
        body_text = driver.find_element(By.TAG_NAME, "body").text[:500]
        print("Page Body Preview:\n", body_text)

    except Exception as e:
        print("❌ Failed to load Reports page:", e)

if __name__ == "__main__":
    driver = configure_driver()
    wait = WebDriverWait(driver, 15)

    try:
        test_page_access(driver, wait)
    finally:
        driver.quit()
