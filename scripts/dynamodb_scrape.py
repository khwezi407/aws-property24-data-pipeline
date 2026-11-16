import requests
from bs4 import BeautifulSoup
import boto3
import hashlib
from datetime import datetime, timezone

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('QuotesTable')

def scrape_quotes():
    url = 'http://quotes.toscrape.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Loop through each quote on the page
    for quote in soup.find_all('div', class_='quote'):
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tags = [tag.text for tag in quote.find_all('a', class_='tag')]

        # Create a unique Quote ID (using sha256 for consistency)
        quote_id = hashlib.sha256(text.encode('utf-8')).hexdigest()

        # Save the quote data to DynamoDB
        table.put_item(
            Item={
                'Quote_id': quote_id,
                'Author_name': author,
                'Quote_text': text,
                'Tags': ", ".join(tags),
                'Scraped_at': str(datetime.now(timezone.utc))
            }
        )
        
    print("Quotes have been scraped and stored in DynamoDB.")

if __name__ == "__main__":
    scrape_quotes()
