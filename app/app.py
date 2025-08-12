from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
from pymongo import MongoClient
from bson import ObjectId
import re
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents'))

# Lazy import function for coordinator
def get_coordinator():
    """Lazy import coordinator to avoid startup delay"""
    try:
        from agents.coordinator import ItineraryCoordinator
        return ItineraryCoordinator
    except ImportError as e:
        print(f"ImportError: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Files in current directory: {os.listdir('.')}")
        if os.path.exists('agents'):
            print(f"Files in agents directory: {os.listdir('agents')}")
        else:
            print("agents directory does not exist")
        return None
    except Exception as e:
        print(f"Unexpected error importing coordinator: {e}")
        import traceback
        traceback.print_exc()
        return None

app = Flask(__name__)

# MongoDB Atlas connection
mongo_uri = "mongodb+srv://TEPIS:TEPIS355@cluster0.lu5p4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["ticketmaster"]
collection = db["events"]

# Function to get all events from MongoDB
def get_all_events():
    try:
        events = list(collection.find())
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
            # Convert datetime objects to string if they exist
            if 'start_date' in event and hasattr(event['start_date'], 'strftime'):
                event['start_date'] = event['start_date'].strftime('%Y-%m-%d')
            if 'end_date' in event and hasattr(event['end_date'], 'strftime'):
                event['end_date'] = event['end_date'].strftime('%Y-%m-%d')
        return events
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return []

# Function to get a single event by ID
def get_event_by_id(event_id):
    try:
        # Your database uses string IDs, not ObjectIds
        event = collection.find_one({"_id": event_id})
        if event:
            event['_id'] = str(event['_id'])
            # Convert datetime objects to string if they exist
            if 'start_date' in event and hasattr(event['start_date'], 'strftime'):
                event['start_date'] = event['start_date'].strftime('%Y-%m-%d')
            if 'end_date' in event and hasattr(event['end_date'], 'strftime'):
                event['end_date'] = event['end_date'].strftime('%Y-%m-%d')
        return event
    except Exception as e:
        print(f"Error getting event by ID: {e}")
        return None

# Cache for events data to avoid repeated database calls
events_cache = None

def get_events_data():
    global events_cache
    if events_cache is None:
        events_cache = get_all_events()
    return events_cache

# Helper function to derive price tier from ticket_price
def get_price_tier_from_ticket_price(ticket_price, event_type=None):
    # First try to extract actual price from ticket_price
    if ticket_price:
        # Handle both string and numeric inputs
        if isinstance(ticket_price, (int, float)):
            price = float(ticket_price)
        else:
            # Extract price number from string like "From $49" or "From $24.91 - $45.76 USD"
            # Try to get the minimum price first
            price_match = re.search(r'\$([0-9,]+(?:\.[0-9]+)?)', str(ticket_price))
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                try:
                    price = float(price_str)
                    # Apply thresholds based on actual data analysis
                    # Data shows: min=$7, median=$35, 75th percentile=$44, 95th percentile=$59, max=$70
                    if price <= 25:
                        return "Moderate"  # Budget-friendly events (below median)
                    elif price <= 45:
                        return "Premium"   # Mid-range events (median to 75th percentile)
                    else:
                        return "Luxury"    # High-end events (above 75th percentile)
                except ValueError:
                    pass
    
    # If no price data available, try to infer from event type
    if event_type:
        event_type_lower = str(event_type).lower()
        
        # Premium/Luxury event types (likely higher cost)
        if any(keyword in event_type_lower for keyword in [
            'arts', 'theatre', 'classical', 'opera', 'ballet', 'jazz', 
            'comedy', 'conference', 'corporate', 'gala', 'festival'
        ]):
            return "Premium"
        
        # Luxury event types (typically most expensive)
        if any(keyword in event_type_lower for keyword in [
            'vip', 'exclusive', 'premier', 'championship', 'playoffs', 'finals'
        ]):
            return "Luxury"
        
        # Moderate event types (typically more accessible pricing)
        if any(keyword in event_type_lower for keyword in [
            'sports', 'music', 'rock', 'pop', 'hip-hop', 'country', 'community',
            'family', 'children', 'outdoor', 'fair', 'market'
        ]):
            return "Moderate"
    
    # Default fallback - distribute remaining events more evenly
    # Instead of putting all in "Others", use a hash-based distribution
    # This gives a more balanced view for filtering purposes
    import hashlib
    if ticket_price or event_type:
        hash_input = str(ticket_price or '') + str(event_type or '')
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % 3
        if hash_value == 0:
            return "Moderate"
        elif hash_value == 1:
            return "Premium"
        else:
            return "Others"  # Keep some in Others for true unknowns
    
    return "Others"

# Mock itinerary data based on the provided structure
itinerary_data = {
    "68433ba8abdc1a99e3304d10": {  # Oktoberfest Munich
        "itinerary": [
            {
                "day": 1,
                "location": "Munich Airport",
                "activities": [
                    {
                        "time": "9:00 AM",
                        "description": "Airport transfer to hotel"
                    },
                    {
                        "time": "2:00 PM",
                        "description": "Historic Munich walking tour"
                    },
                    {
                        "time": "6:00 PM",
                        "description": "Traditional Bavarian dinner"
                    }
                ]
            },
            {
                "day": 2,
                "location": "Oktoberfest Grounds",
                "activities": [
                    {
                        "time": "10:00 AM",
                        "description": "Enter the festival grounds and explore beer halls"
                    },
                    {
                        "time": "12:00 PM",
                        "description": "Traditional Bavarian lunch and beer tasting"
                    },
                    {
                        "time": "3:00 PM",
                        "description": "Enjoy rides and traditional games"
                    }
                ]
            },
            {
                "day": 3,
                "location": "Neuschwanstein Castle",
                "activities": [
                    {
                        "time": "9:00 AM",
                        "description": "Begin your day with a hearty breakfast at a nearby café"
                    },
                    {
                        "time": "10:00 AM",
                        "description": "Explore the magnificent Neuschwanstein Castle and its surroundings"
                    },
                    {
                        "time": "1:00 PM",
                        "description": "Enjoy lunch with panoramic views of the Bavarian Alps"
                    },
                    {
                        "time": "3:30 PM",
                        "description": "Visit the nearby Hohenschwangau Castle"
                    },
                    {
                        "time": "5:30 PM",
                        "description": "Return to Munich for your final evening celebration"
                    }
                ]
            }
        ],
        "highlights": [
            "Traditional Bavarian beer halls",
            "Authentic German cuisine",
            "Folk music and dancing",
            "Historic Munich city tour",
            "Neuschwanstein Castle day trip"
        ],
        "trip_info": {
            "duration": "4 days",
            "category": "culture",
            "price_range": "Moderate",
            "end_date": "Oct 2, 2024"
        }
    }
}

# Helper function to get statistics
def get_stats():
    events = get_events_data()
    total_events = len(events)
    unique_countries = len(set(event.get('country_name', 'Unknown') for event in events if event.get('country_name')))
    # Calculate estimated happy travelers (based on events)
    happy_travelers = min(total_events * 125, 10000)  # Cap at 10k
    
    return {
        'total_events': total_events,
        'countries': unique_countries,
        'happy_travelers': happy_travelers
    }

# Helper function to get filter counts
def get_filter_counts():
    try:
        # Get category counts using aggregation
        category_pipeline = [
            {'$group': {'_id': '$event_type', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        category_results = list(collection.aggregate(category_pipeline))
        categories = {(result['_id'] if result['_id'] else 'Others'): result['count'] for result in category_results}
        
        # Get state counts
        state_pipeline = [
            {'$group': {'_id': '$state_name', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        state_results = list(collection.aggregate(state_pipeline))
        states = {(result['_id'] if result['_id'] else 'Others'): result['count'] for result in state_results}
        
        # Get city counts
        city_pipeline = [
            {'$group': {'_id': '$city_name', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        city_results = list(collection.aggregate(city_pipeline))
        cities = {(result['_id'] if result['_id'] else 'Others'): result['count'] for result in city_results}
        
        # Price tiers are derived in-place
        events = get_events_data()
        price_tiers = {'Others': 0, 'Moderate': 0, 'Premium': 0, 'Luxury': 0}
        
        for event in events:
            price_tier = get_price_tier_from_ticket_price(event.get('ticket_price', None), event.get('event_type', None))
            if price_tier not in price_tiers:
                price_tiers[price_tier] = 0
            price_tiers[price_tier] += 1
        
        return {
            'categories': categories,
            'states': states,
            'cities': cities,
            'price_tiers': price_tiers
        }
    except Exception as e:
        print(f"Error retrieving filters: {e}")
        return {
            'categories': {'Others': 0},
            'states': {'Others': 0},
            'cities': {'Others': 0},
            'price_tiers': {'Others': 0}
        }

@app.route('/')
def home():
    events = get_events_data()
    featured_events = events[:3]  # Show first 3 events as featured
    stats = get_stats()
    return render_template('home.html', featured_events=featured_events, stats=stats)

@app.route('/events')
def events():
    category = request.args.get('category', 'All Categories')
    price_range = request.args.get('price_range', 'All Prices')
    location = request.args.get('location', 'All Locations')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 24  # Show 24 events per page
    
    filtered_events = get_events_data()
    
    # Filter by category (event_type)
    if category and category != 'All Categories':
        filtered_events = [e for e in filtered_events if e.get('event_type') == category or (not e.get('event_type') and category == 'Others')]
    
    # Filter by price range
    if price_range and price_range != 'All Prices':
        filtered_events = [e for e in filtered_events if get_price_tier_from_ticket_price(e.get('ticket_price'), e.get('event_type')) == price_range]
    
    # Filter by location (state or city)
    if location and location != 'All Locations':
        filtered_events = [e for e in filtered_events if 
                          e.get('state_name') == location or 
                          e.get('city_name') == location or 
                          (not e.get('state_name') and not e.get('city_name') and location == 'Others')]
    
    # Search filter
    if search:
        filtered_events = [e for e in filtered_events if 
                          search.lower() in e.get('event_title', '').lower() or 
                          search.lower() in e.get('city_name', '').lower() or
                          search.lower() in e.get('state_name', '').lower()]
    
    # Pagination
    total_events = len(filtered_events)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_events = filtered_events[start:end]
    
    # Calculate pagination info
    total_pages = (total_events + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    # Get filter counts for display
    filter_counts = get_filter_counts()
    
    return render_template('events.html', 
                         events=paginated_events, 
                         total_events=total_events,
                         current_page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         current_category=category,
                         current_price_range=price_range,
                         current_location=location,
                         current_search=search,
                         filter_counts=filter_counts)

@app.route('/event/<event_id>')
def event_detail(event_id):
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    # --- Ensure Trip Info Fields Are Populated for Template ---
    # Duration
    if not event.get('duration'):
        if event.get('start_date') and event.get('end_date') and event['end_date'] != 'None' and event['end_date'] is not None:
            try:
                from datetime import datetime
                start = datetime.strptime(event['start_date'], '%Y-%m-%d')
                end = datetime.strptime(event['end_date'], '%Y-%m-%d')
                delta = (end - start).days + 1
                event['duration'] = f"{delta} days" if delta > 0 else "1 day"
            except Exception:
                event['duration'] = "-"
        else:
            event['duration'] = "-"
    # Category
    if not event.get('category'):
        category = event.get('event_type') or event.get('type')
        event['category'] = category if category else "-"
    # Price tier
    if not event.get('price_tier'):
        event['price_tier'] = get_price_tier_from_ticket_price(event.get('ticket_price'))

    # --- End Ensure Trip Info Fields Are Populated ---

    # Check if this is a trip planner request
    duration = request.args.get('duration')
    cost = request.args.get('cost')
    user_address = request.args.get('user_address')

    if duration and cost:
        # Generate comprehensive trip data using coordinator
        try:
            event_data = {
                'city_name': event.get('city_name', 'Unknown'),
                'duration': duration,
                'cost': cost,
                # Add full event details for itinerary planning
                'event_title': event.get('event_title', 'Event'),
                'event_date': event.get('start_date', ''),
                'event_venue': event.get('venue_name', ''),
                'event_description': event.get('summary', ''),
                'event_time': event.get('event_time', 'Evening')
            }

            print(f"Generating trip data for {event_data['city_name']} - {duration} - {cost}")

            # Get coordinator class using lazy import
            ItineraryCoordinator = get_coordinator()
            if not ItineraryCoordinator:
                raise Exception("Unable to import coordinator")

            coordinator = ItineraryCoordinator(event_data)
            trip_data = coordinator.generate_itinerary()

            # Add trip preferences to the data
            trip_data['trip_preferences'] = {
                'duration': duration,
                'cost': cost
            }
            
            # Calculate home-to-destination routes if user address provided
            home_routes = None
            if user_address and user_address.strip():
                try:
                    print(f"Calculating routes from {user_address} to {event.get('city_name', 'Unknown')}")
                    
                    # Import and use transportation agent
                    from agents.transportation_agent import TransportationAgent
                    transport_agent = TransportationAgent()
                    
                    # Create destination address from event data
                    destination_address = f"{event.get('city_name', '')}, {event.get('state_name', '')}, {event.get('country_name', '')}".strip(', ')
                    
                    home_routes = transport_agent.get_home_to_destination_routes(user_address, destination_address)
                    print(f"Routes calculated successfully from {user_address}")
                    
                except Exception as route_error:
                    print(f"Error calculating home routes: {route_error}")
                    home_routes = None
            
            # Add home routes to trip data
            trip_data['home_routes'] = home_routes

            print(f"Trip data generated successfully for {event_data['city_name']}")

            return render_template('event_detail.html', event=event, trip_data=trip_data, show_trip_plan=True, home_routes=home_routes)
        except Exception as e:
            # Add detailed logging
            print("Error generating trip data:")
            import traceback
            traceback.print_exc()

            # Fall back to basic event display with error message
            itinerary = itinerary_data.get(event_id, {"itinerary": [], "highlights": [], "trip_info": {}})
            return render_template('event_detail.html', event=event, itinerary=itinerary, show_trip_plan=False, error=f"Error generating trip plan: {str(e)}")
    
    # Regular event detail view
    itinerary = itinerary_data.get(event_id, {"itinerary": [], "highlights": [], "trip_info": {}})
    return render_template('event_detail.html', event=event, itinerary=itinerary)

@app.route('/trip-planner/<event_id>')
def trip_planner(event_id):
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404
    
    return render_template('trip_planner.html', event=event)

@app.route('/trip-planner/detailed/<event_id>')
def detailed_trip_planner(event_id):
    """Show the detailed trip planning form"""
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404
    
    return render_template('trip_planner_detailed.html', event=event)

@app.route('/trip-planner/generate/<event_id>', methods=['POST'])
def generate_detailed_trip(event_id):
    """Generate detailed trip plan with context analysis"""
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404
    
    # Get form data
    duration = request.form.get('duration', '3 days')
    budget = request.form.get('budget', 'in-between')
    group_size = request.form.get('group_size', '2')
    user_address = request.form.get('user_address', '')
    detailed_requirements = request.form.get('detailed_requirements', '')
    
    print(f"Processing detailed trip request for {event.get('event_title')}")
    print(f"Requirements: {detailed_requirements[:100]}...")
    
    try:
        # Create enhanced event data
        event_data = {
            'city_name': event.get('city_name', 'Unknown'),
            'duration': duration,
            'cost': budget,
            'group_size': int(group_size),
            'user_address': user_address,
            # Add full event details for itinerary planning
            'event_title': event.get('event_title', 'Event'),
            'event_date': event.get('start_date', ''),
            'event_venue': event.get('event_place', ''),
            'event_description': event.get('summary', ''),
            'event_time': event.get('start_time', 'Evening')
        }
        
        # Import the detailed coordinator
        from agents.coordinator import DetailedItineraryCoordinator
        
        # Create detailed coordinator with requirements
        coordinator = DetailedItineraryCoordinator(event_data, detailed_requirements)
        
        # Generate the detailed itinerary
        trip_data = coordinator.generate_detailed_itinerary()
        
        # Get analysis summary for display
        analysis_summary = coordinator.get_analysis_summary()
        
        # Add trip preferences to the data
        trip_data['trip_preferences'] = {
            'duration': duration,
            'cost': budget,
            'group_size': group_size,
            'user_address': user_address
        }
        
        # Add analysis summary for template display
        trip_data['analysis_summary'] = analysis_summary
        
        # Calculate home-to-destination routes if user address provided
        home_routes = None
        if user_address and user_address.strip():
            try:
                print(f"Calculating routes from {user_address} to {event.get('city_name', 'Unknown')}")
                
                # Import and use transportation agent
                from agents.transportation_agent import TransportationAgent
                transport_agent = TransportationAgent()
                
                # Create destination address from event data
                destination_address = f"{event.get('city_name', '')}, {event.get('state_name', '')}, {event.get('country_name', '')}".strip(', ')
                
                home_routes = transport_agent.get_home_to_destination_routes(user_address, destination_address)
                print(f"Routes calculated successfully from {user_address}")
                
            except Exception as route_error:
                print(f"Error calculating home routes: {route_error}")
                home_routes = None
        
        # Add home routes to trip data
        trip_data['home_routes'] = home_routes
        
        print(f"Detailed trip data generated successfully for {event_data['city_name']}")
        
        return render_template('event_detail.html', event=event, trip_data=trip_data, 
                             show_trip_plan=True, home_routes=home_routes, 
                             is_detailed_plan=True)
        
    except Exception as e:
        # Add detailed logging
        print("Error generating detailed trip data:")
        import traceback
        traceback.print_exc()
        
        # Fall back to basic event display with error message
        return render_template('event_detail.html', event=event, 
                             show_trip_plan=False, 
                             error=f"Error generating detailed trip plan: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
