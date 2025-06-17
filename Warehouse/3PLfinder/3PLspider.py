import time
import random
import pandas as pd
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# SETUP
chrome_driver_path = "./chromedriver-mac-x64/chromedriver"  # Change this to your local path
state = "NY"  # Change this to the state you want to scrape

if state == "NJ":
    start_url = "https://3plfinder.com/search-result/?directory_type=general&q=&in_loc=221"  # NJ
elif state == "CA":
    start_url = "https://3plfinder.com/search-result/?directory_type=general&q=&in_loc=170"  # CA
elif state == "NY":
    start_url = "https://3plfinder.com/search-result/?directory_type=general&q=&in_loc=111" # NY
else:
    raise ValueError("Unsupported state. Please set state to 'NJ', 'CA', or 'NY'.")


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# OPEN PAGE
driver.get(start_url)
time.sleep(random.uniform(3, 5))

results = []
page = 1
visited_pages = set()

def extract_current_page() -> dict:
    """Extract all listings on the current visible page."""
    time.sleep(random.uniform(2, 4))
    listings = driver.find_elements(By.CSS_SELECTOR, "div.directorist-col-6")
    print(f"🔍 Found {len(listings)} listings on current page.")
    for block in listings:
        try:
            name = block.find_element(By.CSS_SELECTOR, "h2.directorist-listing-title a").text.strip()
        except NoSuchElementException:
            name = ""
        try:
            website = block.find_element(By.CSS_SELECTOR, "li.directorist-listing-card-website a").get_attribute("href").strip()
        except NoSuchElementException:
            website = ""
        try:
            address = block.find_element(By.CSS_SELECTOR, "li.directorist-listing-card-address").text.strip()
        except NoSuchElementException:
            address = ""
        try:
            phone = block.find_element(By.CSS_SELECTOR, "li.directorist-listing-card-phone").text.strip()
        except NoSuchElementException:
            phone = ""

        results.append({
            "Name": name,
            "Address": address,
            "Phone": phone,
            "Website": website
        })
        print(f"✅ {name} | {phone} | {website}")

# # First page
# print(f"\n🌐 Scraping Page {1}...")
# extract_current_page()

# Loop through pages
while True:
    
    time.sleep(random.uniform(2, 4))

    try:
        nav_links = driver.find_elements(By.CSS_SELECTOR, "div.nav-links a.page-numbers.haspaglink")
    except NoSuchElementException:
        print("🚫 No pagination links found.")
        break

    # Find the next page that hasn't been visited
    next_page_el = None
    for el in nav_links:
        page_number = el.get_attribute("data-pageurl")
        if page_number and page_number not in visited_pages:
            next_page_el = el
            break

    if not next_page_el:
        print("✅ All pages visited.")
        break

    page_number = next_page_el.get_attribute("data-pageurl")
    visited_pages.add(page_number)
    print(f"\n➡️ Navigating to page {page_number}...")

    # Scroll to pagination then click with JS
    driver.execute_script("arguments[0].scrollIntoView(true);", next_page_el)
    driver.execute_script("arguments[0].click();", next_page_el)
    time.sleep(random.uniform(3, 5))

    extract_current_page()


# CLOSE
driver.quit()

# SAVE TO CSV
df = pd.DataFrame(results)
# df.to_csv("3plfinder_ny.csv", index=False)
# print(f"\n📁 Saved {len(df)} listings to 3plfinder_ny.csv")
file_name = f"{state}_3plfinder.xlsx"
df.to_excel(file_name, index=False)
