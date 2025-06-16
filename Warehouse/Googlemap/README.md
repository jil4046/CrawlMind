# Google Maps Scraper
This is a Google Maps business scraper based on Playwright. 


##  Features

-  Custom keyword search (e.g., “warehouse in New York”)
-  Extracts only key fields: Name, Website, Phone Number
-  Automatically saves results in Excel (.xlsx) and CSV (.csv)
-  Fully CLI-based, supports search term and record count


### 1️⃣ Install Dependencies

Make sure you have Python 3 installed. Using a virtual environment is recommended:

```bash
pip install pandas openpyxl playwright
python -m playwright install
  
