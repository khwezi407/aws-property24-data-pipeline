from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import boto3
import hashlib
from datetime import datetime, timezone
import time

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Property24Listings')

def scrape_property24(max_pages=2):
    """Scrape Property24 listings for a specific area and save to DynamoDB."""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        base_url = 'https://www.property24.com/for-sale/gauteng/1/p'
        url_suffix = '?PropertyCategory=House%2cApartmentOrFlat%2cTownhouse'
        
        for page in range(1, max_pages + 1):
            print(f"--- Scraping page {page} ---")
            driver.get(f"{base_url}{page}{url_suffix}")

            # Wait for the first listing tile to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.p24_content, .p24_tileContainer'))
            )
            
            # Give the page an extra moment to render
            time.sleep(2)

            # Find all property cards on the page
            containers = driver.find_elements(By.CSS_SELECTOR, '.p24_content, .p24_tileContainer')

            for container in containers:
                try:
                    # 1. Extract the price (splitting to avoid mixing with location text)
                    price_raw = container.find_element(By.CSS_SELECTOR, '.p24_price').text
                    price = price_raw.split('\n')[0].strip()

                    # 2. Extract the description (acts as Title)
                    try:
                        description = container.find_element(By.CSS_SELECTOR, '.p24_description').text
                        if " in " in description:
                            title = description.split(" in ")[0].strip()
                        else:
                            title = description
                    except:
                        title = "N/A"

                    # 3. Extract the location
                    try:
                        location = container.find_element(By.CSS_SELECTOR, '.p24_location').text
                    except:
                        location = "N/A"

                    if not price or price == "N/A":
                        continue

                    # Create a unique ID
                    unique_string = f"{title}-{location}-{price}"
                    listing_id = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

                    # Save to DynamoDB
                    table.put_item(
                        Item={
                            'listing_id': listing_id,
                            'title': title,
                            'price': price,
                            'location': location,
                            'scraped_at': str(datetime.now(timezone.utc))
                        }
                    )
                    print(f"Saved: {title} | {price} | {location}")

                except Exception as e:
                    # Skip broken cards
                    continue

            time.sleep(3) # Politeness delay between pages

    finally:
        driver.quit()
        print("Scraping complete. Browser closed.")

if __name__ == "__main__":
    scrape_property24(max_pages=2)
