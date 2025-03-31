# eBay Price Scraper

This script scrapes eBay Australia for listings based on a user-provided search keyword. It extracts details such as the product name, price, postage cost, total cost, condition, brand, model, and other metadata. The results are saved to a CSV file, and key statistics (e.g., lowest price, median price, Q1, Q3) are calculated and logged.

## Features

- **Dynamic Search Keyword**: Accepts a search query via command-line arguments.
- **Pagination Support**: Scrapes multiple pages of results (up to 10 pages by default).
- **Postage Handling**: Automatically calculates total cost by adding price and postage (handles "Free postage").
- **CSV Output**: Saves scraped data to a `listings.csv` file.
- **Statistics Calculation**: Computes and logs key pricing statistics, including Q1 and Q3 values.

## Prerequisites

- Tested with Python 3.11
- Required Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `numpy`

Install the required libraries using pip:

```bash
pip install requests beautifulsoup4 pandas numpy
```

## Usage
Command-Line Arguments
The script requires a -keyword argument to specify the search query.

```bash
python scrape_ebay_listings.py -keyword "RTX 3090"
```

**Example Output**

```bash
2025-03-31 10:00:00 - INFO - Program started.
2025-03-31 10:00:00 - INFO - Reading session data from file...
2025-03-31 10:00:00 - INFO - Session data successfully read.
2025-03-31 10:00:00 - INFO - Starting to scrape eBay listings...
2025-03-31 10:00:01 - INFO - Scraping page 1 with URL: https://www.ebay.com.au/sch/i.html?_nkw=RTX+3090&_sacat=0&LH_BIN=1&_pgn=1
...
2025-03-31 10:00:05 - INFO - Program completed.
```

## Files

1. **scrape_ebay_listings.py** : The main script for scraping eBay listings.
2. **session.txt** : A file containing session data (e.g., cookies, headers) for authenticated requests.
3. **listings.csv** : The output CSV file containing scraped data.

Example **session.txt**
```plaintext
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36
Cookie: ebay=%7B%22session-id%22%3A%221234567890abcdef%22%7D; ...
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Referer: https://www.ebay.com.au/
```

## Finding your Session Cookie
![brave_OxZ3iSmllm](https://github.com/user-attachments/assets/afb205eb-563e-4fa1-b482-0ccbbb03508c)

## Finding your User Agent
![brave_gGNjjIHnY6](https://github.com/user-attachments/assets/81f36b57-4fd2-4812-8943-cb8d6b7188e6)

## Output
The script generates a **listings.csv** file with the following columns:

- **Name** : Product title.
- **Price** : Base price of the product.
- **Postage** : Shipping cost (or 0.0 for free postage).
- **Total Cost** : Sum of price and postage.
- **Condition** : Product condition (e.g., New, Pre-owned).

- **Brand** : Brand of the product.
- **Model** : Model of the product.
- **Others** : Additional details (e.g., memory size).
- **Link** : URL to the product page.

**Example CSV Content**
```csv
Name,Price,Postage,Total Cost,Condition,Brand,Model,Others,Link
NVIDIA GeForce RTX 3090 OC Graphics Card,1500.00,11.35,1511.35,Pre-owned,Graphics,NVIDIA GeForce RTX 3090,24 GB,https://www.ebay.com.au/itm/306203765742
ASUS ROG Strix LC GeForce RTX 3090,1499.99,0.00,1499.99,New,Graphics,ASUS ROG Strix LC GeForce RTX 3090,24 GB GDDR6X,https://www.ebay.com.au/itm/123456789012
```

## Statistics
After scraping, the script calculates and logs the following statistics:

- **Lowest Price**
- **Median Price**
- **Average Price**
- **Maximum Price**
- **Q1 Price (25th Percentile)**
- **Q3 Price (75th Percentile)**
- **Lowest Total Cost**
- **Median Total Cost**
- **Average Total Cost**
- **Maximum Total Cost**
- **Q1 Total Cost (25th Percentile)**
- **Q3 Total Cost (75th Percentile)**

## Troubleshooting
- **HTTP 503 Errors** : If you encounter frequent 503 errors, eBay may be blocking your IP. Use proxy rotation or reduce request frequency.
- **Parsing Errors** : If the script fails to parse certain fields, inspect the HTML structure of the eBay page and update the parsing logic accordingly.
