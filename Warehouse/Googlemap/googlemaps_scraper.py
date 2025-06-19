import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from openpyxl import load_workbook
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----- MAIN -----
service = "warehouse"         # <- edit the keyword
location = "New York"         # <- edit the location

URL = "https://www.google.com/maps"
print("Starting scraping...")

options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)
driver.get(URL)

try:
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button'))).click()
except:
    pass

input_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchboxinput"]')))
input_field.send_keys(service.lower() + ' ' + location.lower())
input_field.send_keys(Keys.ENTER)

print("Waiting for results...")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Nv2PK')))
time.sleep(5)

scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
last_height = 0
while True:
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
    time.sleep(2)
    new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    if new_height == last_height:
        break
    last_height = new_height

soup = BeautifulSoup(driver.page_source, "html.parser")
boxes = soup.find_all('div', class_='Nv2PK')
driver.quit()

print("Collecting business data...")
data = []

for box in boxes:
    try:
        business_name = box.find('div', class_='qBF1Pd').getText()
    except:
    pass
    try:
        phone_number = box.find('span', class_='UsdlK').getText()
    except:
    pass
    try:
        website = box.find('a', class_='lcr4fd').get('href')
    except:
    pass
    try:
        inner_div = box.find_all('div', class_='W4Efsd')[1].find('div', class_='W4Efsd')
        address = [span.text for span in inner_div.find_all('span') if span.text and not span.find('span')][-1]
    except:
    pass

    data.append({
        'Business Name': business_name,
        'Phone Number': phone_number,
        'Email': '',
        'Website': website,
        'Address': address,
        'Source': 'Google Maps'
    })

df = pd.DataFrame(data)

def find_email_in_text(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(pattern, text)
    return emails[0] if emails else None

def check_contact_page(driver, base_url):
    try:
        contact_url = f"{base_url.rstrip('/')}/contact"
        driver.get(contact_url)
        time.sleep(3)
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        return find_email_in_text(page_text)
    except Exception:
        return None

def process_website(website):
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    email = None
    try:
        if website == "N/A":
            return None
        email = check_contact_page(driver, website)
        if not email:
            driver.get(website)
            time.sleep(3)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            page_text = driver.find_element(By.TAG_NAME, "body").text
            email = find_email_in_text(page_text)
        return email if email else None
    except Exception as e:
        print(f"Error processing {website}: {e}")
        return None
    finally:
        driver.quit()

print("Extracting emails from websites...")
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(process_website, row['Website']): index
        for index, row in df.iterrows()
        if row['Website'] != "N/A"
    }
    for future in as_completed(futures):
        index = futures[future]
        try:
            email = future.result()
            df.at[index, 'Email'] = email if email else "Not found"
            print(f"✓ {df.at[index, 'Business Name']} — {email}")
        except Exception as e:
            print(f"Error processing email for index {index}: {e}")

output_file = f"gmap_{location}_{service}.xlsx".replace(" ", "_")
print(f"\n✅ Total businesses scraped: {len(df)}")

df.to_excel(output_file, index=False, engine='openpyxl')
wb = load_workbook(output_file)
ws = wb.active
ws.column_dimensions['A'].width = 30  # Business Name
ws.column_dimensions['B'].width = 18  # Phone Number
ws.column_dimensions['C'].width = 30  # Email
ws.column_dimensions['D'].width = 20  # Website
ws.column_dimensions['E'].width = 20  # address

wb.save(output_file)

print(f"\n✅ All data saved to: {output_file}")

