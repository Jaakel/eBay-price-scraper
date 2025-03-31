import re
import csv
import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Step 1: Read session data from file
def read_session(file_path):
    logging.info("Reading session data from file...")
    session_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(": ", 1)
                session_data[key] = value
        logging.info("Session data successfully read.")
    except Exception as e:
        logging.error(f"Error reading session data: {e}")
    return session_data

# Step 2: Scrape eBay for listings using session
def scrape_ebay_listings(session_data, keyword):
    logging.info("Starting to scrape eBay listings...")
    base_url = "https://www.ebay.com.au/sch/i.html"
    params = {
        "_nkw": keyword,  # Search query from command-line argument
        "_sacat": 0,      # Category ID (0 = all categories)
        "LH_BIN": 1       # Only show "Buy It Now" listings
    }

    headers = {
        "User-Agent": session_data.get("User-Agent", "Mozilla/5.0"),
        "Cookie": session_data.get("Cookie", ""),
        "Accept": session_data.get("Accept", "*/*"),
        "Accept-Language": session_data.get("Accept-Language", "en-US,en;q=0.5"),
        "Referer": session_data.get("Referer", "https://www.ebay.com.au/")
    }

    listings = []
    page_number = 1
    max_pages = 10  # Set a reasonable limit for testing; eBay allows up to 100 pages

    while page_number <= max_pages:
        try:
            # Add pagination parameter to the URL
            params["_pgn"] = page_number
            logging.info(f"Scraping page {page_number} with URL: {base_url}?{params}")

            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  # Raise an error for bad HTTP responses
            logging.info(f"Received response with status code: {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all("div", class_="s-item__info")

            if not items:
                logging.info(f"No more listings found on page {page_number}. Stopping pagination.")
                break

            for item in items:
                try:
                    # Extract title
                    name_tag = item.find("span", role="heading")
                    name = name_tag.text.strip() if name_tag else "N/A"

                    # Extract price
                    price_tag = item.find("span", class_="s-item__price")
                    price_text = price_tag.text.strip() if price_tag else "AU $0.00"
                    price = float(re.sub(r"[^\d\.]", "", price_text.split(" ")[-1]))  # Extract numeric price

                    # Extract postage
                    postage_tag = item.find("span", class_="s-item__shipping")
                    postage_text = postage_tag.text.strip() if postage_tag else "+AU $0.00 postage"
                    
                    # Handle "Free postage" case
                    if "free" in postage_text.lower():
                        postage = 0.0
                    else:
                        postage = float(re.sub(r"[^\d\.]", "", postage_text.split(" ")[-2])) if "postage" in postage_text else 0.0

                    # Calculate total cost
                    total_cost = price + postage

                    # Extract link
                    link_tag = item.find("a", class_="s-item__link")
                    link = link_tag["href"] if link_tag else "N/A"

                    # Extract subtitles (Condition, Brand, Model, etc.)
                    subtitle_tag = item.find("div", class_="s-item__subtitle")
                    subtitles = subtitle_tag.text.strip().split(" · ") if subtitle_tag else ["N/A"]
                    condition = subtitles[0].strip() if len(subtitles) > 0 else "N/A"
                    brand = subtitles[1].strip() if len(subtitles) > 1 else "N/A"
                    model = subtitles[2].strip() if len(subtitles) > 2 else "N/A"
                    others = " · ".join(subtitles[3:]).strip() if len(subtitles) > 3 else "N/A"

                    # Append listing to results
                    listings.append({
                        "Name": name,
                        "Price": price,
                        "Postage": postage,
                        "Total Cost": total_cost,
                        "Condition": condition,
                        "Brand": brand,
                        "Model": model,
                        "Others": others,
                        "Link": link
                    })
                    logging.debug(f"Found listing: {name} - Price: ${price:.2f}, Postage: ${postage:.2f}, Total Cost: ${total_cost:.2f}, Condition: {condition}, Brand: {brand}, Model: {model}, Others: {others}")
                except Exception as e:
                    logging.error(f"Error processing listing: {e}")

            logging.info(f"Successfully scraped {len(items)} listings from page {page_number}.")
            page_number += 1  # Move to the next page

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP request failed: {e}")
            break

    logging.info(f"Pagination completed. Total listings scraped: {len(listings)}.")
    return listings

# Step 3: Save listings to CSV
def save_to_csv(listings, file_path):
    logging.info(f"Saving {len(listings)} listings to CSV file: {file_path}")
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Name", "Price", "Postage", "Total Cost", "Condition", "Brand", "Model", "Others", "Link"])
            writer.writeheader()
            writer.writerows(listings)
        logging.info("Listings successfully saved to CSV.")
    except Exception as e:
        logging.error(f"Error saving listings to CSV: {e}")

# Step 4: Calculate statistics from CSV
def calculate_statistics(file_path):
    logging.info(f"Calculating statistics from CSV file: {file_path}")
    try:
        df = pd.read_csv(file_path)
        prices = df['Price']
        total_costs = df['Total Cost']

        lowest_price = prices.min()
        median_price = prices.median()
        average_price = prices.mean()
        max_price = prices.max()
        q1_price = np.quantile(prices, 0.25)  # First quartile (Q1)
        q3_price = np.quantile(prices, 0.75)  # Third quartile (Q3)

        lowest_total_cost = total_costs.min()
        median_total_cost = total_costs.median()
        average_total_cost = total_costs.mean()
        max_total_cost = total_costs.max()
        q1_total_cost = np.quantile(total_costs, 0.25)  # First quartile (Q1)
        q3_total_cost = np.quantile(total_costs, 0.75)  # Third quartile (Q3)

        stats = {
            "Lowest Price": lowest_price,
            "Median Price": median_price,
            "Average Price": average_price,
            "Maximum Price": max_price,
            "Q1 Price (25th Percentile)": q1_price,
            "Q3 Price (75th Percentile)": q3_price,
            "Lowest Total Cost": lowest_total_cost,
            "Median Total Cost": median_total_cost,
            "Average Total Cost": average_total_cost,
            "Maximum Total Cost": max_total_cost,
            "Q1 Total Cost (25th Percentile)": q1_total_cost,
            "Q3 Total Cost (75th Percentile)": q3_total_cost
        }
        logging.info("Statistics calculated successfully.")
        return stats
    except Exception as e:
        logging.error(f"Error calculating statistics: {e}")
        return {}

# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape eBay listings based on a search keyword.")
    parser.add_argument("-keyword", required=True, help="The search keyword (e.g., 'RTX 3090')")
    args = parser.parse_args()

    logging.info("Program started.")

    # Step 1: Read session data
    session_data = read_session("session.txt")

    # Step 2: Scrape eBay listings
    listings = scrape_ebay_listings(session_data, args.keyword)

    # Step 3: Save listings to CSV
    if listings:
        save_to_csv(listings, "listings.csv")

        # Step 4: Calculate statistics
        stats = calculate_statistics("listings.csv")
        if stats:
            logging.info("Price Statistics:")
            for key, value in stats.items():
                logging.info(f"{key}: {value:.2f}")
    else:
        logging.warning("No listings were scraped. Exiting program.")

    logging.info("Program completed.")

if __name__ == "__main__":
    main()