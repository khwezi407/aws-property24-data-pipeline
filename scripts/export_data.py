import boto3
import csv

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Property24Listings')

def export_to_csv():
    print("Scanning DynamoDB table...")
    
    # Scan the table to get all items
    response = table.scan()
    items = response['Items']

    # Write to a CSV file
    with open('property_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write headers
        writer.writerow(['Listing ID', 'Title', 'Price', 'Location', 'Scraped At'])
        
        # Write data rows
        for item in items:
            writer.writerow([
                item.get('listing_id', ''), 
                item.get('title', ''), 
                item.get('price', ''), 
                item.get('location', ''), 
                item.get('scraped_at', '')
            ])

    print(f"Successfully exported {len(items)} records to property_data.csv")

if __name__ == "__main__":
    export_to_csv()
