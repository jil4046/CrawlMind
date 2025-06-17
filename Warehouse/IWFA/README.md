# IWFA Scrapper
scrapes public [IWFA](https://www.findawarehouse.org/SearchFAW) listings for New York (NY), New Jersey (NJ) or California (CA) and saves the results to Excel.
## Requirements
- Python 3.7+
- `pip install -r requirements.txt`
## Usage
1. Clone the repository:
2. Set up `chromedriver` in your PATH or specify the path in the script.
3. Change `state` to valid values: `NY`, `NJ`, or `CA`.
4. Run the script:
## Output
.xlsx file with the following columns:
- `Company Name`
- `Address`
- `Phone`
- `Website`