#  Google Maps Business Email Scraper

This Python script allows you to:

✅ Search for businesses on **Google Maps** by keyword and location  
✅ Automatically extract each business's:
- Name
- Phone number
- Website
- Email (from their website)

Results are saved in a neatly formatted Excel file like:

```
gmap_location_service.xlsx
```

---

## Features

- Uses **Selenium** to interact with Google Maps
- Extracts emails from `/contact` pages or homepage
- Supports **multithreading** for fast email extraction
- Clean Excel output with formatted column widths

---

## 📦 Dependencies

run on terminal:

```bash
pip install pandas beautifulsoup4 selenium openpyxl
```

---

##  Requirements

| Component     | Description                                |
|---------------|--------------------------------------------|
| Python        | 3.8 or higher                              |
| Chrome        | Installed on your system                   |
| ChromeDriver  | Matches your Chrome version and is in PATH |

### Install ChromeDriver

1. Go to: https://chromedriver.chromium.org/downloads  
2. Find your Chrome version and download matching driver  
3. Place the `chromedriver` binary in your PATH (e.g. `/usr/local/bin` or project root)

**Optional for macOS (Homebrew):**

```bash
brew install chromedriver
```

---

## 🚀 How to Use

### 1. Modify Keyword and Location

Open the script and update these two lines:

```python
service = "warehouse"
location = "New York"
```

You can change `"warehouse"` to `"catering"`, `"coffee shop"`, etc.  
And change `"New York"` to any city or country.

---

### 2. Run the Script

```bash
python gmap_scraper.py
```

---

## 📁 Output Format

A file like this will be generated:

```
gmap_New_York_warehouse.xlsx
```

With the following columns:

| Business Name     | Phone Number     | Email            | Website                |
|-------------------|------------------|------------------|------------------------|
| Example Inc.      | (123) 456-7890   | info@example.com | https://example.com    |
| Another Company   | N/A              | Not found        | https://acompany.com   |

---

## ⚠️ Notes

- Emails are found by visiting each business's website:
  - First tries `/contact`
  - Falls back to homepage if needed
- "Not found" is shown if no email is located
- Excel columns are auto-formatted for readability
- Some websites may block automated access (rare)
