from pymongo import MongoClient
import os
from datetime import datetime

def create_events_collection():
    # Connect to MongoDB
    # Using environment variables for security, but falling back to localhost if not set
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    
    # Create or get the database (you can change 'events_db' to your preferred database name)
    db = client['TEPIS']

    # Create or get the events collection
    events_collection = db['events']

    # Create an index on event_title for better query performance
    events_collection.create_index('event_title')

    # Example document schema
    sample_event = {
        'event_title': '',
        'summary': '',
        'image_url': '',
        'language': '',
        'event_type': '',
        'event_host': '',
        'ticket_price': None,  # Can be float or string depending on your needs
        'booking_url': '',
        'start_date': None,  # Will be datetime object
        'end_date': None,    # Will be datetime object
        'start_time': '',
        'end_time': '',
        'event_place': '',
        'full_address': '',
        'country_name': '',
        'state_name': '',
        'city_name': '',
        'postal_code': ''
    }
    
    # Insert a sample document to test the collection
    test_event = sample_event.copy()
    test_event.update({
        'event_title': 'Test Event',
        'summary': 'This is a test event',
        'language': 'English',
        'event_type': 'Conference',
        'event_host': 'Test Organization',
        'ticket_price': '100 USD',
        'start_date': datetime.now(),
        'end_date': datetime.now(),
        'start_time': '10:00 AM',
        'end_time': '5:00 PM',
        'event_place': 'Test Venue',
        'full_address': '123 Test Street',
        'country_name': 'Test Country',
        'state_name': 'Test State',
        'city_name': 'Test City',
        'postal_code': '12345'
    })
    events_collection.insert_one(test_event)
    print("Sample event has been inserted!")

    print("Events collection has been created successfully!")
    return events_collection

def fetch_event(event_title=None):
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    
    # Get the database and collection
    db = client['TEPIS']
    events_collection = db['events']
    
    # If event_title is provided, fetch specific event, otherwise fetch first event
    if event_title:
        event = events_collection.find_one({'event_title': event_title})
    else:
        event = events_collection.find_one()
    
    if event:
        print("\nFound event:")
        for key, value in event.items():
            if key != '_id':  # Skip the MongoDB ID
                print(f"{key}: {value}")
    else:
        print("No events found in the collection.")
    
    return event

if __name__ == "__main__":
    # First create the collection and insert sample data
    create_events_collection()
    
    # Then fetch and display the test event
    print("\nFetching the test event:")
    fetch_event()
# This script initializes the MongoDB database and creates the events collection.
# It can be run directly to set up the database.