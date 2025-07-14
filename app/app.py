from flask import Flask, render_template, request
from datetime import datetime
import re

app = Flask(__name__)

# Mock events data (replace with your own or load from a file)
mock_events = [
    {
        '_id': '68433ba8abdc1a99e3304d10',
        'event_title': 'Oktoberfest Munich',
        'event_type': 'Festival',
        'country_name': 'Germany',
        'state_name': 'Bavaria',
        'city_name': 'Munich',
        'ticket_price': 'From $49',
        'start_date': '2024-09-29',
        'end_date': '2024-10-02'
    }
    # Add more mock events as needed
]

# Function to get all events (mocked)
def get_all_events():
    return mock_events

# Function to get a single event by ID (mocked)
def get_event_by_id(event_id):
    for event in mock_events:
        if event['_id'] == event_id:
            return event
    return None

# Cache for events data to avoid repeated calls
events_cache = None

def get_events_data():
    global events_cache
    if events_cache is None:
        events_cache = get_all_events()
    return events_cache

# Helper function to derive price tier from ticket_price
def get_price_tier_from_ticket_price(ticket_price):
    if not ticket_price:
        return "Others"
    if isinstance(ticket_price, (int, float)):
        price = float(ticket_price)
    else:
        price_match = re.search(r'\$([0-9,]+)', str(ticket_price))
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            try:
                price = float(price_str)
            except ValueError:
                return "Others"
        else:
            return "Others"
    if price <= 100:
        return "Moderate"
    elif price <= 500:
        return "Premium"
    else:
        return "Luxury"

# Mock itinerary data
itinerary_data = {
    "68433ba8abdc1a99e3304d10": {
        "itinerary": [
            {
                "day": 1,
                "location": "Munich Airport",
                "activities": [
                    {"time": "9:00 AM", "description": "Airport transfer to hotel"},
                    {"time": "2:00 PM", "description": "Historic Munich walking tour"},
                    {"time": "6:00 PM", "description": "Traditional Bavarian dinner"}
                ]
            },
            {
                "day": 2,
                "location": "Oktoberfest Grounds",
                "activities": [
                    {"time": "10:00 AM", "description": "Enter the festival grounds and explore beer halls"},
                    {"time": "12:00 PM", "description": "Traditional Bavarian lunch and beer tasting"},
                    {"time": "3:00 PM", "description": "Enjoy rides and traditional games"}
                ]
            },
            {
                "day": 3,
                "location": "Neuschwanstein Castle",
                "activities": [
                    {"time": "9:00 AM", "description": "Begin your day with a hearty breakfast at a nearby café"},
                    {"time": "10:00 AM", "description": "Explore the magnificent Neuschwanstein Castle and its surroundings"},
                    {"time": "1:00 PM", "description": "Enjoy lunch with panoramic views of the Bavarian Alps"},
                    {"time": "3:30 PM", "description": "Visit the nearby Hohenschwangau Castle"},
                    {"time": "5:30 PM", "description": "Return to Munich for your final evening celebration"}
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
    happy_travelers = min(total_events * 125, 10000)
    return {
        'total_events': total_events,
        'countries': unique_countries,
        'happy_travelers': happy_travelers
    }

# Helper function to get filter counts
def get_filter_counts():
    events = get_events_data()
    # Categories
    categories = {}
    for event in events:
        cat = event.get('event_type', 'Others') or 'Others'
        categories[cat] = categories.get(cat, 0) + 1
    # States
    states = {}
    for event in events:
        state = event.get('state_name', 'Others') or 'Others'
        states[state] = states.get(state, 0) + 1
    # Cities
    cities = {}
    for event in events:
        city = event.get('city_name', 'Others') or 'Others'
        cities[city] = cities.get(city, 0) + 1
    # Price tiers
    price_tiers = {'Others': 0, 'Moderate': 0, 'Premium': 0, 'Luxury': 0}
    for event in events:
        price_tier = get_price_tier_from_ticket_price(event.get('ticket_price', None))
        if price_tier not in price_tiers:
            price_tiers[price_tier] = 0
        price_tiers[price_tier] += 1
    return {
        'categories': categories,
        'states': states,
        'cities': cities,
        'price_tiers': price_tiers
    }

@app.route('/')
def home():
    events = get_events_data()
    featured_events = events[:3]
    stats = get_stats()
    return render_template('home.html', featured_events=featured_events, stats=stats)

@app.route('/events')
def events():
    category = request.args.get('category', 'All Categories')
    price_range = request.args.get('price_range', 'All Prices')
    location = request.args.get('location', 'All Locations')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 24

    filtered_events = get_events_data()

    if category and category != 'All Categories':
        filtered_events = [e for e in filtered_events if e.get('event_type') == category or (not e.get('event_type') and category == 'Others')]
    if price_range and price_range != 'All Prices':
        filtered_events = [e for e in filtered_events if get_price_tier_from_ticket_price(e.get('ticket_price')) == price_range]
    if location and location != 'All Locations':
        filtered_events = [e for e in filtered_events if
                          e.get('state_name') == location or
                          e.get('city_name') == location or
                          (not e.get('state_name') and not e.get('city_name') and location == 'Others')]
    if search:
        filtered_events = [e for e in filtered_events if
                          search.lower() in e.get('event_title', '').lower() or
                          search.lower() in e.get('city_name', '').lower() or
                          search.lower() in e.get('state_name', '').lower()]

    total_events = len(filtered_events)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_events = filtered_events[start:end]
    total_pages = (total_events + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
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
    itinerary = itinerary_data.get(event_id, {"itinerary": [], "highlights": [], "trip_info": {}})
    return render_template('event_detail.html', event=event, itinerary=itinerary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)