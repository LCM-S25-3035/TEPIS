from pymongo import MongoClient
import os
from datetime import datetime, timedelta

def add_sample_events():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    db = client['TEPIS']
    events_collection = db['events']

    # Clear existing events
    events_collection.delete_many({})

    # Sample events data
    events = [
        {
            'event_title': 'Summer Music Festival',
            'summary': 'Experience the best of electronic and indie music',
            'image_url': '',
            'language': 'English',
            'event_type': 'Festival',
            'event_host': 'City Events Inc.',
            'ticket_price': 'From $49',
            'booking_url': 'http://example.com/summer-fest',
            'start_date': datetime.now() + timedelta(days=9),  # June 15
            'end_date': datetime.now() + timedelta(days=10),
            'start_time': '2:00 PM',
            'end_time': '11:00 PM',
            'event_place': 'Central Park',
            'full_address': '123 Park Avenue',
            'country_name': 'United States',
            'state_name': 'New York',
            'city_name': 'New York City',
            'postal_code': '10022'
        },
        {
            'event_title': 'Tech Innovation Summit',
            'summary': 'Join industry leaders in technology and innovation',
            'image_url': '',
            'language': 'English',
            'event_type': 'Conference',
            'event_host': 'Tech Forums',
            'ticket_price': 'From $199',
            'booking_url': 'http://example.com/tech-summit',
            'start_date': datetime.now() + timedelta(days=12),  # June 18
            'end_date': datetime.now() + timedelta(days=13),
            'start_time': '9:00 AM',
            'end_time': '6:00 PM',
            'event_place': 'Convention Center',
            'full_address': '456 Tech Street',
            'country_name': 'United States',
            'state_name': 'California',
            'city_name': 'San Francisco',
            'postal_code': '94103'
        },
        {
            'event_title': 'Art & Culture Exhibition',
            'summary': 'Discover contemporary art from around the world',
            'image_url': '',
            'language': 'English',
            'event_type': 'Exhibition',
            'event_host': 'City Gallery',
            'ticket_price': 'From $25',
            'booking_url': 'http://example.com/art-expo',
            'start_date': datetime.now() + timedelta(days=5),
            'end_date': datetime.now() + timedelta(days=15),
            'start_time': '10:00 AM',
            'end_time': '8:00 PM',
            'event_place': 'City Gallery',
            'full_address': '789 Art Avenue',
            'country_name': 'United States',
            'state_name': 'Illinois',
            'city_name': 'Chicago',
            'postal_code': '60601'
        },
        {
            'event_title': 'Food & Wine Festival',
            'summary': 'Taste exotic cuisines and premium wines',
            'image_url': '',
            'language': 'English',
            'event_type': 'Festival',
            'event_host': 'Culinary Association',
            'ticket_price': 'From $75',
            'booking_url': 'http://example.com/food-fest',
            'start_date': datetime.now() + timedelta(days=15),
            'end_date': datetime.now() + timedelta(days=17),
            'start_time': '12:00 PM',
            'end_time': '10:00 PM',
            'event_place': 'City Square',
            'full_address': '321 Food Street',
            'country_name': 'United States',
            'state_name': 'Texas',
            'city_name': 'Austin',
            'postal_code': '78701'
        },
        {
            'event_title': 'International Film Festival',
            'summary': 'Showcasing the best international and independent films',
            'image_url': '',
            'language': 'Multiple',
            'event_type': 'Festival',
            'event_host': 'World Cinema Association',
            'ticket_price': 'From $15 per screening',
            'booking_url': 'http://example.com/film-fest',
            'start_date': datetime.now() + timedelta(days=20),
            'end_date': datetime.now() + timedelta(days=27),
            'start_time': '11:00 AM',
            'end_time': '11:00 PM',
            'event_place': 'Grand Cinema Complex',
            'full_address': '567 Cinema Boulevard',
            'country_name': 'United States',
            'state_name': 'California',
            'city_name': 'Los Angeles',
            'postal_code': '90028'
        },
        {
            'event_title': 'Yoga and Wellness Retreat',
            'summary': 'Three-day immersive wellness experience with expert instructors',
            'image_url': '',
            'language': 'English',
            'event_type': 'Retreat',
            'event_host': 'Mindful Living Co.',
            'ticket_price': '$399 all-inclusive',
            'booking_url': 'http://example.com/yoga-retreat',
            'start_date': datetime.now() + timedelta(days=25),
            'end_date': datetime.now() + timedelta(days=27),
            'start_time': '7:00 AM',
            'end_time': '8:00 PM',
            'event_place': 'Mountain View Resort',
            'full_address': '789 Serenity Road',
            'country_name': 'United States',
            'state_name': 'Colorado',
            'city_name': 'Boulder',
            'postal_code': '80302'
        },
        {
            'event_title': 'Gaming Convention 2025',
            'summary': 'The biggest gaming event of the year with latest releases and tournaments',
            'image_url': '',
            'language': 'English',
            'event_type': 'Convention',
            'event_host': 'GamersUnite',
            'ticket_price': 'From $45',
            'booking_url': 'http://example.com/gaming-con',
            'start_date': datetime.now() + timedelta(days=30),
            'end_date': datetime.now() + timedelta(days=32),
            'start_time': '10:00 AM',
            'end_time': '9:00 PM',
            'event_place': 'Tech Convention Center',
            'full_address': '123 Gamer Street',
            'country_name': 'United States',
            'state_name': 'Washington',
            'city_name': 'Seattle',
            'postal_code': '98101'
        },
        {
            'event_title': 'Comedy Night Spectacular',
            'summary': 'An evening of laughter with top stand-up comedians',
            'image_url': '',
            'language': 'English',
            'event_type': 'Entertainment',
            'event_host': 'Laugh Factory',
            'ticket_price': '$35',
            'booking_url': 'http://example.com/comedy-night',
            'start_date': datetime.now() + timedelta(days=7),
            'end_date': datetime.now() + timedelta(days=7),
            'start_time': '8:00 PM',
            'end_time': '11:00 PM',
            'event_place': 'City Comedy Club',
            'full_address': '456 Laugh Lane',
            'country_name': 'United States',
            'state_name': 'New York',
            'city_name': 'New York City',
            'postal_code': '10019'
        },
        {
            'event_title': 'Business Leadership Summit',
            'summary': 'Connect with industry leaders and learn about future business trends',
            'image_url': '',
            'language': 'English',
            'event_type': 'Conference',
            'event_host': 'Business Leaders Association',
            'ticket_price': 'From $299',
            'booking_url': 'http://example.com/business-summit',
            'start_date': datetime.now() + timedelta(days=40),
            'end_date': datetime.now() + timedelta(days=41),
            'start_time': '9:00 AM',
            'end_time': '5:00 PM',
            'event_place': 'Grand Hotel Conference Center',
            'full_address': '789 Business Plaza',
            'country_name': 'United States',
            'state_name': 'Massachusetts',
            'city_name': 'Boston',
            'postal_code': '02110'
        },
        {
            'event_title': 'Classical Music Symphony',
            'summary': 'A night of classical masterpieces performed by the City Symphony Orchestra',
            'image_url': '',
            'language': 'English',
            'event_type': 'Concert',
            'event_host': 'City Symphony Orchestra',
            'ticket_price': 'From $65',
            'booking_url': 'http://example.com/symphony',
            'start_date': datetime.now() + timedelta(days=14),
            'end_date': datetime.now() + timedelta(days=14),
            'start_time': '7:30 PM',
            'end_time': '10:00 PM',
            'event_place': 'Symphony Hall',
            'full_address': '123 Orchestra Avenue',
            'country_name': 'United States',
            'state_name': 'Illinois',
            'city_name': 'Chicago',
            'postal_code': '60604'
        },
        {
            'event_title': 'Photography Workshop',
            'summary': 'Learn advanced photography techniques from professional photographers',
            'image_url': '',
            'language': 'English',
            'event_type': 'Workshop',
            'event_host': 'Creative Arts Institute',
            'ticket_price': '$149',
            'booking_url': 'http://example.com/photo-workshop',
            'start_date': datetime.now() + timedelta(days=18),
            'end_date': datetime.now() + timedelta(days=18),
            'start_time': '10:00 AM',
            'end_time': '4:00 PM',
            'event_place': 'Creative Studio',
            'full_address': '321 Artist Way',
            'country_name': 'United States',
            'state_name': 'Oregon',
            'city_name': 'Portland',
            'postal_code': '97205'
        }
    ]

    # Insert the events
    events_collection.insert_many(events)
    print(f"Added {len(events)} sample events to the database!")

if __name__ == "__main__":
    add_sample_events()
