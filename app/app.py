#!/usr/bin/env python3
"""
Main application module for the Flask web application.
"""

from flask import Flask, render_template, request, redirect, url_for, send_from_directory,jsonify
import os
from datetime import datetime
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Load configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# MongoDB connection
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client['TEPIS']
events_collection = db['events']

def get_featured_events():
    """Get featured events from MongoDB"""
    return list(events_collection.find().limit(6))

def get_upcoming_events():
    """Get upcoming events from MongoDB"""
    current_date = datetime.now()
    return list(events_collection.find({
        'start_date': {'$gte': current_date}
    }).sort('start_date', 1).limit(9))

@app.route('/')
def index():
    featured_events = get_featured_events()
    upcoming_events = get_upcoming_events()
    
    return render_template('index.html', 
                         featured_events=featured_events,
                         upcoming_events=upcoming_events)

@app.route('/events')
def events():
    current_date = datetime.now()
    page = request.args.get('page', 1, type=int)
    per_page = 7  # Number of events per page

    # Get total count for pagination
    total_events = events_collection.count_documents({'start_date': {'$gte': current_date}})
    
    # Get events for current page
    events_list = list(events_collection.find({
        'start_date': {'$gte': current_date}
    }).sort('start_date', 1).skip((page - 1) * per_page).limit(per_page))
    
    # Calculate total pages
    total_pages = (total_events + per_page - 1) // per_page
    
    # Get categories (event_types) with counts
    pipeline_categories = [
        {
            '$group': {
                '_id': '$event_type',
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id': 1}  # Sort alphabetically
        }
    ]
    categories = list(events_collection.aggregate(pipeline_categories))
    
    # Get locations (cities) with counts
    pipeline_locations = [
        {
            '$group': {
                '_id': '$city_name',
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id': 1}  # Sort alphabetically
        }
    ]
    locations = list(events_collection.aggregate(pipeline_locations))
    
    return render_template('events.html', 
                         events=events_list,
                         current_page=page,
                         total_pages=total_pages,
                         categories=categories,
                         locations=locations,
                         total_events=total_events)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        # Here you would typically handle login/authentication
        username = request.form.get('username')
        password = request.form.get('password')
        # Add your authentication logic here
        return redirect(url_for('index'))
    return render_template('auth.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/events')
def filter_events():
    """API endpoint for filtered events"""
    try:
        current_date = datetime.now()
        
        # Get raw filter parameters and log them
        category = request.args.get('category')
        location = request.args.get('location')
        print(f"Raw filter parameters - category: {category}, location: {location}")
        
        # Build the filter query starting with date filter
        query = {'start_date': {'$gte': current_date}}
        
        # Add category filter if provided and not 'all'
        if category and category.lower() != 'all':
            query['event_type'] = category
            print(f"Added category filter: {category}")
            
        # Add location filter if provided and not 'all'
        if location and location.lower() != 'all':
            query['city_name'] = location
            print(f"Added location filter: {location}")
            
        print(f"Final MongoDB query: {query}")
        
        # First get all events to check available data
        all_events = list(events_collection.find({'start_date': {'$gte': current_date}}))
        print(f"Total events in database: {len(all_events)}")
        if all_events:
            print(f"Available event types: {set(e.get('event_type') for e in all_events)}")
            print(f"Available locations: {set(e.get('city_name') for e in all_events)}")
        
        # Get filtered events
        filtered_events = list(events_collection.find(query).sort('start_date', 1))
        print(f"Number of events after filtering: {len(filtered_events)}")
        
        # Convert ObjectId and datetime objects to string for JSON serialization
        for event in filtered_events:
            event['_id'] = str(event['_id'])
            if isinstance(event['start_date'], datetime):
                event['start_date'] = event['start_date'].isoformat()
            if isinstance(event['end_date'], datetime):
                event['end_date'] = event['end_date'].isoformat()
            print(f"Matched event: {event.get('event_title')} - Type: {event.get('event_type')} in {event.get('city_name')}")
        
        response_data = {
            'events': filtered_events,
            'total': len(filtered_events),
            'filters_applied': {
                'category': category,
                'location': location
            },
            'query_used': str(query)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in filter_events: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'events': [],
            'total': 0
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])
