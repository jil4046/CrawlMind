import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import ast
'''
Batch process multiple excel files to extract emails from websites.
The script will 
'''
# Change file_list to the actual paths of your Excel files
file_list = [    
    './3PLfinder/3plfinder_CA.csv',
    './3PLfinder/3plfinder_NJ.csv'
    './3PLfinder/3plfinder_NY.csv',
    './IWFA/IWLA_CA.csv',
    './IWFA/IWLA_NJ.csv',
    './IWFA/IWLA_NY.csv'
    # 'Book1.csv',
    ]
# Change this if your column name is different
website_column = 'Website'  




def extract_emails_from_html(html):
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')

    # --- 1. Extract emails from mailto: links (as before)
    mailto_emails = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'mailto:' in href:
            email = href.replace('mailto:', '').split('?')[0]
            mailto_emails.append(email)

    # --- 2. Extract emails from visible text (as before)
    visible_text = soup.get_text(" ", strip=True)
    text_emails = re.findall(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b", visible_text)
    print(f"Found {text_emails} emails in visible text.")

    # --- 3. NEW: Extract emails from raw HTML source (e.g. JS onclick, script tags)
    html_emails = re.findall(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b", html)
    print(f"Found {html_emails} emails in raw HTML source.")

    # 4. Emails from obfuscated JS (eval(unescape(...)))
    unescape_emails = []
    unescape_blocks = re.findall(r"eval\(unescape\('([^']+)'\)\)", html)
    for encoded in unescape_blocks:
        decoded = unquote(encoded)
        found = re.findall(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", decoded)
        unescape_emails.extend(found)
    print(f"Found {unescape_emails} emails in obfuscated JS.")
    # --- Combine all, deduplicate
    all_emails = set(mailto_emails + text_emails + html_emails)
        # 6. Filter out unwanted domains
    filtered_emails = [
        e for e in all_emails
        if not (
            e.lower().endswith('.png') or
            e.lower().endswith('.jpg') or
            e.lower().endswith('.jpeg') or
            e.lower().endswith('.webp') or
            re.search('%',e) or
            re.search('@sentry', e) or
            re.search(r'@[0-9.]', e)  # IP-style domain
        )
    ]
    return filtered_emails

def try_fetch_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to load {url}: {e}")
        return None


def extract_emails_with_contact_fallback(base_url):
    # Try the base URL first
    html = try_fetch_url(base_url)
    if html:
        emails = extract_emails_from_html(html)
        if emails:
            return emails
        # Try /contact and /contact-us pages
        for suffix in ["contact", "contact-us"]:
            contact_url = urljoin(base_url, suffix)
            print(f"↪ Trying contact page: {contact_url}")
            html = try_fetch_url(contact_url)
            if html:
                print(f"↪ Extracting emails from: {contact_url}")
                emails = extract_emails_from_html(html)
                if emails:
                    return emails
    return []


def extract_first_valid_email(email_field):
    # Convert string-represented list to actual list
    if isinstance(email_field, str):
        try:
            email_list = ast.literal_eval(email_field)
        except:
            return ""
    elif isinstance(email_field, list):
        email_list = email_field
    else:
        return ""

    # Extract the first valid (non-empty) email
    for email in email_list:
        if email and isinstance(email, str) and email.strip():
            return email.strip()
            
    return ""  # Return blank if no valid email found



# Batch process for each file
for file_name in file_list:
    df = pd.read_csv(file_name)
    print(f"Processing file: {file_name}")
    # Get emails from the first URL
    all_emails = []
    first_emails = []
    for website in df['Website']:    
        print(f"Processing {website}...")
        emails = extract_emails_with_contact_fallback(website)
        # if emails:
        #     print(f"Found emails: {emails}")
        # else:
        #     print("No emails found.")
        email = extract_first_valid_email(emails)
        all_emails.append(emails) 
        first_emails.append(email)
        print("\n")  # Add a newline for better readability between websites
    print(first_emails)
    df['All_Emails'] = all_emails
    df['Email'] = first_emails
    df.to_csv(file_name, index=False)