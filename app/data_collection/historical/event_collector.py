import requests
import time
import json
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import os
import sys
from typing import Dict, List, Optional, Set
import hashlib

class EventCollector:
    def __init__(self):
        # MongoDB setup
        self.mongo_uri = "mongodb+srv://TEPIS:TEPIS355@cluster0.lu5p4.mongodb.net/?retryWrites=true\u0026w=majority\u0026appName=Cluster0"
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client["ticketmaster"]
        self.events_collection = self.db["events"]
        self.progress_collection = self.db["collection_progress"]
        
        # API setup
        self.API_KEY = "8KksxMa6GpWB9jGyVAKjGAANlXNMtqo9"
        self.API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
        
        # Rate limiting (Ticketmaster allows 5000 requests per day, 5 per second)
        self.requests_per_second = 4  # Conservative limit
        self.max_requests_per_day = 4500  # Conservative daily limit
        self.request_count = 0
        self.last_request_time = 0
        self.session_start_time = time.time()
        
        # Progress tracking
        self.progress_file = "collection_progress.json"
        self.log_file = "event_collection.log"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load US and Canadian cities/states
        self.locations = self.load_locations()
        
        # Track processed events to avoid duplicates
        self.processed_event_ids = set()
        
        # Statistics
        self.session_stats = {
            'events_collected': 0,
            'events_skipped': 0,
            'duplicates_found': 0,
            'invalid_events': 0,
            'locations_processed': 0,
            'api_requests': 0
        }
        
    def load_locations(self) -> List[Dict]:
        """Load US and Canadian cities/states for data collection"""
        # Major US cities by state
        us_locations = [
            {"city": "New York", "state": "NY", "country": "US"},
            {"city": "Los Angeles", "state": "CA", "country": "US"},
            {"city": "Chicago", "state": "IL", "country": "US"},
            {"city": "Houston", "state": "TX", "country": "US"},
            {"city": "Phoenix", "state": "AZ", "country": "US"},
            {"city": "Philadelphia", "state": "PA", "country": "US"},
            {"city": "San Antonio", "state": "TX", "country": "US"},
            {"city": "San Diego", "state": "CA", "country": "US"},
            {"city": "Dallas", "state": "TX", "country": "US"},
            {"city": "San Jose", "state": "CA", "country": "US"},
            {"city": "Austin", "state": "TX", "country": "US"},
            {"city": "Jacksonville", "state": "FL", "country": "US"},
            {"city": "Fort Worth", "state": "TX", "country": "US"},
            {"city": "Columbus", "state": "OH", "country": "US"},
            {"city": "Charlotte", "state": "NC", "country": "US"},
            {"city": "San Francisco", "state": "CA", "country": "US"},
            {"city": "Indianapolis", "state": "IN", "country": "US"},
            {"city": "Seattle", "state": "WA", "country": "US"},
            {"city": "Denver", "state": "CO", "country": "US"},
            {"city": "Washington", "state": "DC", "country": "US"},
            {"city": "Boston", "state": "MA", "country": "US"},
            {"city": "Las Vegas", "state": "NV", "country": "US"},
            {"city": "Nashville", "state": "TN", "country": "US"},
            {"city": "Oklahoma City", "state": "OK", "country": "US"},
            {"city": "Louisville", "state": "KY", "country": "US"},
            {"city": "Portland", "state": "OR", "country": "US"},
            {"city": "Milwaukee", "state": "WI", "country": "US"},
            {"city": "Albuquerque", "state": "NM", "country": "US"},
            {"city": "Tucson", "state": "AZ", "country": "US"},
            {"city": "Fresno", "state": "CA", "country": "US"},
            {"city": "Sacramento", "state": "CA", "country": "US"},
            {"city": "Mesa", "state": "AZ", "country": "US"},
            {"city": "Kansas City", "state": "MO", "country": "US"},
            {"city": "Atlanta", "state": "GA", "country": "US"},
            {"city": "Long Beach", "state": "CA", "country": "US"},
            {"city": "Colorado Springs", "state": "CO", "country": "US"},
            {"city": "Raleigh", "state": "NC", "country": "US"},
            {"city": "Miami", "state": "FL", "country": "US"},
            {"city": "Virginia Beach", "state": "VA", "country": "US"},
            {"city": "Omaha", "state": "NE", "country": "US"},
            {"city": "Oakland", "state": "CA", "country": "US"},
            {"city": "Minneapolis", "state": "MN", "country": "US"},
            {"city": "Tulsa", "state": "OK", "country": "US"},
            {"city": "Arlington", "state": "TX", "country": "US"},
            {"city": "Tampa", "state": "FL", "country": "US"},
            {"city": "New Orleans", "state": "LA", "country": "US"},
            {"city": "Wichita", "state": "KS", "country": "US"},
            {"city": "Cleveland", "state": "OH", "country": "US"},
            {"city": "Bakersfield", "state": "CA", "country": "US"},
            {"city": "Aurora", "state": "CO", "country": "US"},
            {"city": "Anaheim", "state": "CA", "country": "US"},
        ]
        
        # Major Canadian cities by province
        canadian_locations = [
            {"city": "Toronto", "state": "ON", "country": "CA"},
            {"city": "Montreal", "state": "QC", "country": "CA"},
            {"city": "Vancouver", "state": "BC", "country": "CA"},
            {"city": "Calgary", "state": "AB", "country": "CA"},
            {"city": "Edmonton", "state": "AB", "country": "CA"},
            {"city": "Ottawa", "state": "ON", "country": "CA"},
            {"city": "Mississauga", "state": "ON", "country": "CA"},
            {"city": "Winnipeg", "state": "MB", "country": "CA"},
            {"city": "Hamilton", "state": "ON", "country": "CA"},
            {"city": "Quebec City", "state": "QC", "country": "CA"},
            {"city": "Halifax", "state": "NS", "country": "CA"},
            {"city": "London", "state": "ON", "country": "CA"},
            {"city": "Kitchener", "state": "ON", "country": "CA"},
            {"city": "Victoria", "state": "BC", "country": "CA"},
            {"city": "Saskatoon", "state": "SK", "country": "CA"},
            {"city": "Regina", "state": "SK", "country": "CA"},
            {"city": "Windsor", "state": "ON", "country": "CA"},
            {"city": "Kelowna", "state": "BC", "country": "CA"},
            {"city": "Barrie", "state": "ON", "country": "CA"},
            {"city": "Sudbury", "state": "ON", "country": "CA"},
        ]
        
        return us_locations + canadian_locations
    
    def rate_limit_check(self):
        """Implement rate limiting to respect API limits"""
        current_time = time.time()
        
        # Check if we need to wait between requests
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < (1.0 / self.requests_per_second):
            sleep_time = (1.0 / self.requests_per_second) - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Check daily limit
        if self.request_count >= self.max_requests_per_day:
            self.logger.warning(f"Daily request limit reached: {self.request_count}")
            return False
        
        return True
    
    def load_progress(self) -> Dict:
        """Load progress from database or file"""
        try:
            # Try loading from MongoDB first
            progress_doc = self.progress_collection.find_one({"_id": "current_progress"})
            if progress_doc:
                return progress_doc
            
            # Fallback to file
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading progress: {e}")
        
        # Return default progress
        return {
            "_id": "current_progress",
            "current_location_index": 0,
            "current_page": 0,
            "last_run_date": None,
            "total_events_collected": 0,
            "processed_locations": []
        }
    
    def save_progress(self, progress: Dict):
        """Save progress to database and file"""
        try:
            # Save to MongoDB
            self.progress_collection.replace_one(
                {"_id": "current_progress"},
                progress,
                upsert=True
            )
            
            # Save to file as backup
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving progress: {e}")
    
    def is_valid_event(self, event_data: Dict) -> bool:
        """Check if event has sufficient data (not too many null values)"""
        required_fields = [
            'event_title', 'start_date', 'event_place', 
            'city_name', 'state_name', 'country_name'
        ]
        
        important_fields = [
            'summary', 'image_url', 'event_type', 'booking_url',
            'full_address', 'postal_code'
        ]
        
        # Check required fields
        for field in required_fields:
            if not event_data.get(field) or event_data[field] in [None, "", "null"]:
                return False
        
        # Check that at least 50% of important fields have values
        valid_important_fields = 0
        for field in important_fields:
            if event_data.get(field) and event_data[field] not in [None, "", "null"]:
                valid_important_fields += 1
        
        if valid_important_fields < (len(important_fields) * 0.5):
            return False
        
        return True
    
    def generate_event_hash(self, event_data: Dict) -> str:
        """Generate a unique hash for event to detect duplicates"""
        # Create hash based on title, date, and venue
        key_data = f"{event_data.get('event_title', '')}" \
                  f"{event_data.get('start_date', '')}" \
                  f"{event_data.get('event_place', '')}" \
                  f"{event_data.get('city_name', '')}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def transform_event_data(self, raw_event: Dict) -> Dict:
        """Transform raw API response to our event format"""
        try:
            # Extract venue information
            venue = raw_event.get('_embedded', {}).get('venues', [{}])[0] if raw_event.get('_embedded', {}).get('venues') else {}
            
            # Extract dates
            dates = raw_event.get('dates', {})
            start_info = dates.get('start', {})
            
            # Extract price information
            price_ranges = raw_event.get('priceRanges', [])
            ticket_price = None
            if price_ranges:
                min_price = price_ranges[0].get('min', 0)
                max_price = price_ranges[0].get('max', 0)
                currency = price_ranges[0].get('currency', 'USD')
                if min_price and max_price:
                    ticket_price = f"From ${min_price} - ${max_price} {currency}"
                elif min_price:
                    ticket_price = f"From ${min_price} {currency}"
            
            # Extract images
            images = raw_event.get('images', [])
            image_url = None
            if images:
                # Get the highest quality image
                for img in images:
                    if img.get('ratio') == '16_9' and img.get('width', 0) >= 1024:
                        image_url = img.get('url')
                        break
                if not image_url:
                    image_url = images[0].get('url')
            
            # Extract classification
            classifications = raw_event.get('classifications', [{}])
            classification = classifications[0] if classifications else {}
            
            event_data = {
                '_id': raw_event.get('id'),
                'event_title': raw_event.get('name', ''),
                'summary': raw_event.get('info', '') or raw_event.get('pleaseNote', ''),
                'image_url': image_url,
                'language': raw_event.get('locale', 'en-us'),
                'event_type': classification.get('segment', {}).get('name', ''),
                'event_host': raw_event.get('promoter', {}).get('name') if raw_event.get('promoter') else None,
                'ticket_price': ticket_price,
                'booking_url': raw_event.get('url', ''),
                'start_date': start_info.get('localDate', ''),
                'end_date': dates.get('end', {}).get('localDate'),
                'start_time': start_info.get('localTime', ''),
                'end_time': dates.get('end', {}).get('localTime'),
                'event_place': venue.get('name', ''),
                'full_address': venue.get('address', {}).get('line1', '') if venue.get('address') else '',
                'country_name': venue.get('country', {}).get('name', '') if venue.get('country') else '',
                'state_name': venue.get('state', {}).get('name', '') if venue.get('state') else '',
                'city_name': venue.get('city', {}).get('name', '') if venue.get('city') else '',
                'postal_code': venue.get('postalCode', ''),
                'collected_at': datetime.now().isoformat()
            }
            
            return event_data
        except Exception as e:
            self.logger.error(f"Error transforming event data: {e}")
            return None
    
    def fetch_events_for_location(self, location: Dict, page: int = 0) -> Optional[Dict]:
        """Fetch events for a specific location"""
        if not self.rate_limit_check():
            return None
        
        params = {
            'apikey': self.API_KEY,
            'city': location['city'],
            'stateCode': location['state'],
            'countryCode': location['country'],
            'page': page,
            'size': 50,  # Maximum per page
            'sort': 'date,asc'
        }
        
        try:
            response = requests.get(self.API_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Fetched page {page} for {location['city']}, {location['state']}")
            
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed for {location['city']}, {location['state']}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            return None
    
    def process_events_batch(self, events: List[Dict]) -> int:
        """Process a batch of events and store valid ones"""
        processed_count = 0
        
        for raw_event in events:
            try:
                # Transform event data
                event_data = self.transform_event_data(raw_event)
                if not event_data:
                    self.session_stats['events_skipped'] += 1
                    continue
                
                # Check if event is valid
                if not self.is_valid_event(event_data):
                    self.session_stats['invalid_events'] += 1
                    continue
                
                # Check for duplicates
                event_hash = self.generate_event_hash(event_data)
                if event_hash in self.processed_event_ids:
                    self.session_stats['duplicates_found'] += 1
                    continue
                
                # Check if already exists in database
                existing_event = self.events_collection.find_one({'_id': event_data['_id']})
                if existing_event:
                    self.session_stats['duplicates_found'] += 1
                    continue
                
                # Insert into database
                self.events_collection.insert_one(event_data)
                self.processed_event_ids.add(event_hash)
                processed_count += 1
                self.session_stats['events_collected'] += 1
                
                # Log every 10th event to avoid spam
                if processed_count % 10 == 0:
                    print(f"  ✓ Stored {processed_count} events so far...")
                
            except DuplicateKeyError:
                # Event already exists, skip
                self.session_stats['duplicates_found'] += 1
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                continue
        
        return processed_count
    
    def print_progress_header(self):
        """Print a nice header for the collection process"""
        print("\n" + "="*80)
        print("             🎟️  TICKETMASTER EVENT DATA COLLECTOR  🎟️")
        print("="*80)
        print(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total locations to process: {len(self.locations)}")
        print(f"API rate limit: {self.requests_per_second} requests/second")
        print(f"Daily limit: {self.max_requests_per_day} requests")
        print("="*80 + "\n")
    
    def print_session_stats(self):
        """Print current session statistics"""
        elapsed_time = time.time() - self.session_start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        print(f"\n📊 SESSION STATISTICS:")
        print(f"   • Events collected: {self.session_stats['events_collected']}")
        print(f"   • Events skipped: {self.session_stats['events_skipped']}")
        print(f"   • Invalid events: {self.session_stats['invalid_events']}")
        print(f"   • Duplicates found: {self.session_stats['duplicates_found']}")
        print(f"   • API requests made: {self.request_count}")
        print(f"   • Session duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"   • Remaining API calls: {self.max_requests_per_day - self.request_count}")
        
        if self.session_stats['events_collected'] > 0:
            rate = self.session_stats['events_collected'] / elapsed_time * 60  # events per minute
            print(f"   • Collection rate: {rate:.1f} events/minute")
        print()
    
    def collect_events(self, max_locations: int = None, test_mode: bool = False):
        """Main collection method"""
        self.print_progress_header()
        
        # Load progress
        progress = self.load_progress()
        start_location_index = progress.get('current_location_index', 0)
        
        # Limit locations for testing
        locations_to_process = self.locations[start_location_index:]
        if max_locations:
            locations_to_process = locations_to_process[:max_locations]
        
        if test_mode:
            locations_to_process = locations_to_process[:2]  # Test with only 2 locations
            print("🧪 TEST MODE: Processing only 2 locations\n")
        
        total_events_collected = progress.get('total_events_collected', 0)
        
        print(f"📍 Starting from location index: {start_location_index}")
        print(f"📦 Total events in database: {total_events_collected}")
        print(f"🎯 Locations to process: {len(locations_to_process)}\n")
        
        for location_index, location in enumerate(locations_to_process):
            if self.request_count >= self.max_requests_per_day:
                print(f"⚠️  Daily request limit reached ({self.request_count}/{self.max_requests_per_day})")
                break
            
            current_location_num = start_location_index + location_index + 1
            print(f"🌍 [{current_location_num}/{len(self.locations)}] Processing: {location['city']}, {location['state']}, {location['country']}")
            
            page = 0
            location_events_collected = 0
            
            while True:
                # Show progress for API requests
                print(f"  📡 Fetching page {page + 1}... (API call {self.request_count + 1})")
                
                # Fetch events for this location and page
                response_data = self.fetch_events_for_location(location, page)
                if not response_data:
                    print(f"  ❌ No response for page {page + 1}")
                    break
                
                # Get events from response
                events = response_data.get('_embedded', {}).get('events', [])
                if not events:
                    print(f"  ℹ️  No events found on page {page + 1}")
                    break
                
                # Show page info
                page_info = response_data.get('page', {})
                total_pages = page_info.get('totalPages', 1)
                total_elements = page_info.get('totalElements', 0)
                
                print(f"  📄 Page {page + 1}/{total_pages} | Total events available: {total_elements}")
                
                # Process events
                processed_count = self.process_events_batch(events)
                location_events_collected += processed_count
                total_events_collected += processed_count
                
                if processed_count > 0:
                    print(f"  ✅ Processed {processed_count} valid events from this page")
                else:
                    print(f"  ⚠️  No valid events found on this page")
                
                # Check if there are more pages
                if page >= total_pages - 1:
                    break
                
                page += 1
                
                # Save progress periodically
                current_progress = {
                    "_id": "current_progress",
                    "current_location_index": start_location_index + location_index,
                    "current_page": page,
                    "last_run_date": datetime.now().isoformat(),
                    "total_events_collected": total_events_collected,
                    "processed_locations": progress.get('processed_locations', []) + [location]
                }
                self.save_progress(current_progress)
                
                if test_mode and location_events_collected >= 5:  # Limit for testing
                    print(f"  🧪 Test mode limit reached for this location")
                    break
            
            print(f"  📊 Location summary: {location_events_collected} events collected")
            self.session_stats['locations_processed'] += 1
            
            # Show session stats every 5 locations
            if (location_index + 1) % 5 == 0:
                self.print_session_stats()
        
        # Final progress save
        final_progress = {
            "_id": "current_progress",
            "current_location_index": start_location_index + len(locations_to_process),
            "current_page": 0,
            "last_run_date": datetime.now().isoformat(),
            "total_events_collected": total_events_collected,
            "processed_locations": progress.get('processed_locations', []) + locations_to_process
        }
        self.save_progress(final_progress)
        
        # Final statistics
        print("\n" + "="*80)
        print("                    🎉 COLLECTION COMPLETED 🎉")
        print("="*80)
        self.print_session_stats()
        
        print(f"📈 Total events in database: {total_events_collected}")
        print(f"🌍 Locations processed this session: {self.session_stats['locations_processed']}")
        print(f"⏰ Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        return total_events_collected

def main():
    """Main function for production data collection"""
    import sys
    
    collector = EventCollector()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Test mode with limited locations
            events_collected = collector.collect_events(max_locations=2, test_mode=True)
            print(f"Test completed. Events collected: {events_collected}")
        elif sys.argv[1] == "--limited":
            # Limited production run (10 locations)
            events_collected = collector.collect_events(max_locations=10, test_mode=False)
            print(f"Limited collection completed. Events collected: {events_collected}")
        else:
            print("Usage: python event_collector.py [--test|--limited]")
            print("  --test: Run in test mode (2 locations only)")
            print("  --limited: Run with 10 locations only")
            print("  (no args): Run full production collection")
    else:
        # Full production run
        events_collected = collector.collect_events()
        print(f"Full collection completed. Events collected: {events_collected}")

if __name__ == "__main__":
    main()
