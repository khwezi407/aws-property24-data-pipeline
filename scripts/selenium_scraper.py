from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import boto3
import hashlib
from datetime import datetime, timezone

# Setup Selenium Chrome Driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('QuotesTable')

try:
    # Open the DYNAMIC website (notice the /js/ at the end)
    url = 'http://quotes.toscrape.com/js/'
    driver.get(url)

    # Wait up to 10 seconds for the JavaScript to load the quotes
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'quote'))
    )

    # Find all quotes on the page
    quotes_elements = driver.find_elements(By.CLASS_NAME, 'quote')

    # Extract and store data
    for quote_element in quotes_elements:
        text = quote_element.find_element(By.CLASS_NAME, 'text').text
        author = quote_element.find_element(By.CLASS_NAME, 'author').text
        tags = [tag.text for tag in quote_element.find_elements(By.CLASS_NAME, 'tag')]

        # Create a unique Quote ID
        quote_id = hashlib.sha256(text.encode('utf-8')).hexdigest()

        # Save data to DynamoDB
        table.put_item(
            Item={
                'Quote_id': quote_id,
                'Author_name': author,
                'Quote_text': text,
                'Tags': ", ".join(tags),
                'Scraped_at': str(datetime.now(timezone.utc))
            }
        )

    print(f"Successfully scraped {len(quotes_elements)} dynamic quotes and stored them in DynamoDB.")

finally:
    # Close the browser
    driver.quit()
