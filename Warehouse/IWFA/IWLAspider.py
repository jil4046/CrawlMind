import time
import random
import csv
import openpyxl
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import Select

# Select the state
state_value = "NY"  # Change to desired state's abbreviation

# ===== CONFIGURE YOUR CHROMEDRIVER PATH HERE =====
chrome_driver_path = "/Users/adiacheng1/Library/CloudStorage/OneDrive-Personal/ApplicationDoc/AIintern/chromedriver-mac-x64/chromedriver"  # Replace with your actual path

# ===== CHROME OPTIONS FOR BETTER ANTI-DETECTION =====
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# ===== INITIALIZE DRIVER =====
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Inject anti-detection JavaScript before any page loads
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
})

# ===== OPEN WEBSITE =====
url = "https://www.findawarehouse.org/SearchFAW"
driver.get(url)

select = Select(driver.find_element(By.ID, "selectState"))
select.select_by_value(state_value)
print(f" Filtered results for state: {state_value}")
time.sleep(random.uniform(3, 5))

results = []
page_number = 1
seen_warehouses = set()  # Avoid duplicate titles

while True:  # Limit to 3 pages
    print(f"\n Processing Page {page_number}...")

    warehouse_blocks = driver.find_elements(By.CSS_SELECTOR, "div.shadow.rounded-4.bg-white.mb-3")

    if not warehouse_blocks:
        print(" No warehouse entries found. Possibly last page.")
        break

    for idx, block in enumerate(warehouse_blocks, start=1):
        text = block.text.strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        if len(lines) < 2:
            continue  # Skip empty or malformed entries

        name = lines[0]
        if name in seen_warehouses:
            continue
        seen_warehouses.add(name)

        location = lines[1] if len(lines) > 1 else ""
        phone = ""
        website = ""
        
        for i, line in enumerate(lines):
            if "Phone" in line and i + 1 < len(lines):
                phone = lines[i + 1]
            if "Website" in line and i + 1 < len(lines):
                website = lines[i + 1]
        
        results.append({
            "Name": name,
            "Address": location,
            "Phone": phone,
            "Website": website
        })

        print(f"📦 {idx}: {name} | {location} | {phone} | {website}")

    # Try to click the “Next” button
    try:
        next_btn = driver.find_element(By.LINK_TEXT, "next")
        if "disabled" in next_btn.get_attribute("class"):
            print(" Reached last page.")
            break

        next_btn.click()
        page_number += 1
        time.sleep(random.uniform(4, 7))

    except NoSuchElementException:
        print(" No 'Next' button found. Finished.")
        break
    except ElementClickInterceptedException:
        print(" Failed to click 'Next' button. Ending.")
        break

# ===== CLOSE BROWSER =====
driver.quit()

# # ===== SAVE TO CSV =====
# csv_file = state_value+"_warehouse_info.csv"
# with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=["Name", "Address", "Phone", "Website"])
#     writer.writeheader()
#     writer.writerows(results)

# print(f"\n Scraping complete! {len(results)} warehouses saved to '{csv_file}'")

# ===== SAVE TO EXCEL =====
excel_file = f"{state_value}_warehouse_info.xlsx"

df = pd.DataFrame(results)     # results is your list of dicts
df.to_excel(excel_file, index=False)

print(f"\nScraping complete! {len(results)} warehouses saved to '{excel_file}'")
