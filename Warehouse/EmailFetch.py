import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import ast


file_list = [    
    './3PLfinder/CA_3plfinder.xlsx',
    './3PLfinder/NJ_3plfinder.xlsx',
    './3PLfinder/NY_3plfinder.xlsx',
    './IWFA/CA_warehouse_info.xlsx',
    './IWFA/NJ_warehouse_info.xlsx',
    './IWFA/NY_warehouse_info.xlsx',
    ]




def extract_emails_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Emails in mailto links
    mailto_emails = [
        a['href'].replace('mailto:', '').split("?")[0]
        for a in soup.find_all('a', href=True)
        if 'mailto:' in a['href']
    ]

    # Inline text emails
    text = soup.get_text(" ", strip=True)
    inline_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)

    return list(set(mailto_emails + inline_emails))


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


# for file_name in file_list:
#     df = pd.read_excel(file_name)
#     print(f"Processing file: {file_name}")
#     # Get emails from the first URL
#     all_emails = []
#     for website in df['Website']:    
#         print(f"Processing {website}...")
#         emails = extract_emails_with_contact_fallback(website)
#         # if emails:
#         #     print(f"Found emails: {emails}")
#         # else:
#         #     print("No emails found.")
#         all_emails.append(emails)        
#         print("\n")  # Add a newline for better readability between websites

#     df['Emails'] = all_emails
#     df.to_excel(file_name, index=False)

for file_name in file_list:
    df = pd.read_excel(file_name)
    df['Email'] = df['Emails'].apply(extract_first_valid_email)
    df.to_excel(file_name, index=False)
    print(f"Updated {file_name} with first valid emails.")