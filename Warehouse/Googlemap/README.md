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
  
# 🗺️ Google Maps Scraper (Simplified Version)

An improved Google Maps business scraper using Playwright. This version only extracts **Business Name**, **Website**, and **Phone Number** for a cleaner and faster experience.

---

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/gmapscraper-improved.git
    cd gmapscraper-improved
    ```

2. **Create and activate a virtual environment** *(optional but recommended)*:

    ```bash
    python -m venv venv
    source venv/bin/activate     # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    Make sure your `requirements.txt` includes:

    ```text
    playwright
    pandas
    openpyxl
    ```

4. **Install Playwright browsers:**

    ```bash
    python -m playwright install
    ```

---

## Usage

1. **Search with one keyword:**

    ```bash
    python main.py -s "warehouse in New York" -t 10
    ```

    - `-s`: search keyword  
    - `-t`: number of businesses to scrape

2. **Search with multiple keywords (via input.txt):**

    Create a file named `input.txt`, add one search term per line:

    ```
    warehouse in New York
    warehouse in California
    ```

    Then run:

    ```bash
    python main.py -t 5
    ```

---

## Output

Scraped results are saved in the `output/` folder, in both `.xlsx` and `.csv` formats.

Example:

