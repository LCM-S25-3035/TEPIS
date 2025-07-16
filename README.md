# TEPIS Web App

## Turn Events Into Epic Adventures

A modern Flask web application for discovering and booking event-based travel experiences.

## Features

- **Home Page**: Hero section with featured events and "How It Works" section
- **Events Page**: Browse and filter events by category, price range, and country
- **Event Detail Page**: Detailed itinerary view with day-by-day activities
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Purple gradient theme with clean card-based design

## Project Structure

```
tepis_webapp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── home.html
│   ├── events.html
│   └── event_detail.html
└── static/               # Static files
    ├── css/
    │   └── style.css     # Main stylesheet
    ├── js/
    │   └── main.js       # JavaScript functionality
    └── images/           # Image assets (empty for now)
```

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd C:\Users\kruna\tepis_webapp
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Pages

### Home Page (/)
- Hero section with gradient background
- Featured events grid
- Statistics row (500+ events, 50+ countries, 10k+ travelers)
- How It Works section with 4 steps

### Events Page (/events)
- Search and filter functionality
- Event cards with category badges
- Responsive grid layout
- Results count display

### Event Detail Page (/event/<event_id>)
- Event hero section with breadcrumbs
- Day-by-day itinerary with timeline
- Trip highlights sidebar
- Booking information

## Data Structure

The application uses mock data based on the provided JSON structure:

```json
{
  "_id": "unique_event_id",
  "event_title": "Event Name",
  "summary": "Event description",
  "image_url": "image_filename.jpg",
  "language": "English",
  "event_type": "Festival/Conference/Sports",
  "event_host": "Host Organization",
  "ticket_price": "From $X",
  "booking_url": "http://booking-link.com",
  "start_date": "2025-06-15",
  "end_date": "2025-06-16",
  "start_time": "2:00 PM",
  "end_time": "11:00 PM",
  "event_place": "Venue Name",
  "full_address": "Full Address",
  "country_name": "Country",
  "state_name": "State",
  "city_name": "City",
  "postal_code": "12345",
  "category": "music/sports/culture",
  "price_tier": "moderate/luxury/premium",
  "duration": "X days"
}
```

## Customization

### Adding New Events
Edit the `events_data` array in `app.py` to add more events.

### Adding Itineraries
Edit the `itinerary_data` dictionary in `app.py` to add detailed itineraries for specific events.

### Styling
Modify `static/css/style.css` to customize the appearance. The design uses:
- Primary color: #8B5CF6 (purple)
- Secondary color: #A855F7 (light purple)
- Accent color: #F59E0B (orange)

### JavaScript
Add interactive features by modifying `static/js/main.js`.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Modern CSS Grid and Flexbox
- **Icons**: Unicode emojis for simplicity
- **Responsive**: Mobile-first design approach

## Future Enhancements

- MongoDB Atlas integration for real data
- User authentication and profiles
- Payment integration
- Real-time availability checking
- Email notifications
- Admin dashboard for event management
- Image upload and management
- Search optimization
- Social sharing features

## License

This project is created for educational purposes.

## Support

For questions or issues, please contact: hello@tepis.com
