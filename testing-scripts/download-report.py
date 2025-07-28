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

def download_report(driver, wait, report_id):
    # Search report
    search_box = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='search' and @aria-controls='DataTables_Table_0']")
        )
    )
    search_box.clear()
    search_box.send_keys(str(report_id))
    print(f"🔍 Entered '{report_id}' into search box.")
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)

    # Click Actions dropdown
    actions_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(), 'Actions') and contains(@class, 'dropdown-toggle')]")
        )
    )
    actions_button.click()
    print(f"⚙️ Clicked 'Actions' dropdown for report {report_id}.")

    # Click Export Excel .xlsx link
    export_xpath = f"//a[@href='/R{report_id}/export/xlsx' and contains(text(), 'Export Excel .xlsx')]"
    export_option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, export_xpath)
        )
    )
    export_option.click()
    print(f"📁 Clicked 'Export Excel .xlsx' for report {report_id}.")

    # Wait for download to finish
    time.sleep(10)

def get_latest_excel_file():
    download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    xlsx_files = [f for f in os.listdir(download_dir) if f.endswith(".xlsx")]
    if not xlsx_files:
        print("❌ No .xlsx files found in Downloads.")
        return None
    latest_file = max(
        [os.path.join(download_dir, f) for f in xlsx_files],
        key=os.path.getctime
    )
    print(f"📄 Latest downloaded Excel file: {latest_file}")
    return latest_file

def print_excel_columns(filepath):
    df = pd.read_excel(filepath)
    print("🧾 Column names in Excel file:")
    print(df.columns.tolist())
    return df

# Setup Chrome options for GitHub Actions (headless mode)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # Disabling GPU acceleration in headless mode
chrome_options.add_argument("--no-sandbox")  # Required for CI environments
chrome_options.add_argument("--start-maximized")

# Initialize Chrome driver (using webdriver_manager for GitHub Actions)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    wait = WebDriverWait(driver, 20)

    # Step 1: Open the Comcast Workflow URL
    driver.get("https://workflow.cable.comcast.com/D262")

    # Step 2: Click Comcast SSO login button (this assumes the button can be identified by its image src)
    sso_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='image' and contains(@src, 'comcast_stack_logo_button.png')]")
        )
    )
    sso_button.click()
    print("✅ Clicked Comcast SSO button.")

    # Step 3: Handle Login
    # If the login page requires entering credentials, we need to fill them out. Update the selectors as needed.
    # Assume the login form has input fields with names "username" and "password"
    username_input = wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_input = wait.until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    
    username_input.send_keys("your_username_here")  # Replace with your username or use secrets
    password_input.send_keys("your_password_here")  # Replace with your password or use secrets
    
    password_input.send_keys(Keys.ENTER)
    print("✅ Submitted credentials.")

    # Step 4: Wait for login to complete and the page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)

    # Step 5: Open the Reports tab directly (you can skip this if you want to go directly to the reports page)
    driver.get("https://workflow.cable.comcast.com/reporting")
    print("✅ Opened 'Reports' tab.")

    # Step 6: Download Report 7271
    download_report(driver, wait, 7271)
    latest_file = get_latest_excel_file()
    if latest_file:
        df_7271 = print_excel_columns(latest_file)

    # Step 7: Download Report 7272
    download_report(driver, wait, 7272)
    latest_file = get_latest_excel_file()
    if latest_file:
        df_7272 = print_excel_columns(latest_file)

finally:
    driver.quit()
    print("🧹 Closed browser.")
