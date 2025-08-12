"""
Itinerary Agent for generating day-by-day activity plans
"""

import os
import json
import time
import hashlib
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

class ItineraryAgent:
    def __init__(self, api_token=None):
        # Set API token from parameter or use fallback for testing
        if api_token:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_token
        
        # Initialize model
        self.endpoint = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            task="text-generation",
            max_new_tokens=1024,
            temperature=0.7
        )
        self.llm = ChatHuggingFace(llm=self.endpoint)
        
        # Cache for responses
        self.cache = {}
        
        # Prompt template for event-centered itinerary
        self.prompt_template = PromptTemplate.from_template("""
Create a {days}-day itinerary for {destination} centered around the main event: "{event_title}". 

Event Details:
- Event: {event_title}
- Date: {event_date}
- Venue: {event_venue}
- Description: {event_description}

The itinerary should:
1. Include the actual event on the appropriate day (preferably day {main_event_day})
2. Plan complementary activities around the event
3. Consider pre-event and post-event activities
4. Include sightseeing and local attractions on other days

Return ONLY JSON in this exact format:

{{
  "itinerary": [
    {{
      "day": 1,
      "location": "Area Name",
      "activities": [
        {{
          "time": "8:00 AM",
          "description": "Start your day with breakfast at a local café"
        }},
        {{
          "time": "10:00 AM",
          "description": "Visit the main attraction"
        }}
      ]
    }}
  ],
  "highlights": [
    "{event_title}",
    "Top attraction 1",
    "Top attraction 2"
  ],
  "trip_info": {{
    "duration": "{days} days",
    "category": "event-centered",
    "price_range": "Moderate"
  }}
}}

Only return valid JSON, no additional text.
""")
        
        self.chain = self.prompt_template | self.llm

    def _get_cache_key(self, destination, days):
        """Generate cache key for destination and days"""
        return hashlib.md5(f"itinerary_{destination}_{days}".lower().encode()).hexdigest()

    def _is_cache_valid(self, cache_entry):
        """Check if cache entry is still valid (24 hours)"""
        if not cache_entry:
            return False
        
        cached_time = cache_entry.get('timestamp', 0)
        return time.time() - cached_time < 86400  # 24 hours

    def _validate_json(self, data):
        """Validate itinerary JSON structure"""
        if not isinstance(data, dict):
            return False
        
        if 'itinerary' not in data:
            return False
        
        if not isinstance(data['itinerary'], list):
            return False
        
        for day in data['itinerary']:
            if not all(field in day for field in ['day', 'location', 'activities']):
                return False
            
            if not isinstance(day['activities'], list):
                return False
            
            for activity in day['activities']:
                if not all(field in activity for field in ['time', 'description']):
                    return False
        
        return True

    def _get_fallback_data(self, destination, days, event_details=None):
        """Fallback data if AI fails"""
        try:
            num_days = int(days)
        except:
            num_days = 1
        
        fallback_activities = []
        
        # Determine event day (middle day for multi-day trips)
        if event_details and num_days > 1:
            event_day = min(2, (num_days + 1) // 2)
        else:
            event_day = 1
        
        for day in range(1, num_days + 1):
            # Regular activities for most days
            activities = [
                {
                    "time": "9:00 AM",
                    "description": f"Start day {day} with breakfast at a local café"
                },
                {
                    "time": "10:30 AM",
                    "description": f"Explore the main attractions of {destination}"
                },
                {
                    "time": "1:00 PM",
                    "description": "Lunch at a recommended restaurant"
                },
                {
                    "time": "3:00 PM",
                    "description": f"Visit cultural sites and museums in {destination}"
                },
                {
                    "time": "6:00 PM",
                    "description": "Dinner and evening activities"
                }
            ]
            
            # Add the actual event on the designated day
            if event_details and day == event_day:
                event_title = event_details.get('title', 'Special Event')
                event_venue = event_details.get('venue', 'Local Venue')
                event_time = event_details.get('time', 'Evening')
                
                # Replace evening activity with the actual event
                activities[-1] = {
                    "time": "7:00 PM",
                    "description": f"Attend {event_title} at {event_venue}"
                }
                
                # Add pre-event preparation
                activities.insert(-1, {
                    "time": "5:00 PM",
                    "description": f"Prepare for {event_title} - dinner and getting ready"
                })
            
            day_activities = {
                "day": day,
                "location": event_details.get('venue', f"{destination} City Center") if event_details and day == event_day else f"{destination} City Center",
                "activities": activities
            }
            fallback_activities.append(day_activities)
        
        # Create highlights with event included
        highlights = []
        if event_details:
            highlights.append(event_details.get('title', 'Special Event'))
        highlights.extend([
            f"Historic {destination} Downtown",
            f"{destination} Cultural District", 
            f"Local {destination} Cuisine",
            f"{destination} Scenic Views"
        ])
        
        return {
            "itinerary": fallback_activities,
            "highlights": highlights,
            "trip_info": {
                "duration": f"{days} days",
                "category": "event-centered" if event_details else "tourism",
                "price_range": "Moderate"
            }
        }

    def generate_itinerary(self, destination, days="1", event_details=None, additional_context=""):
        """Generate itinerary for destination and duration centered around an event with optional context"""
        cache_key = self._get_cache_key(destination, days + additional_context)
        
        # Check cache first
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']
        
        try:
            # Prepare event details for prompt
            if event_details:
                event_title = event_details.get('title', 'Event')
                event_date = event_details.get('date', '')
                event_venue = event_details.get('venue', '')
                event_description = event_details.get('description', '')
                
                # Calculate which day the event should be on (middle day for multi-day trips)
                try:
                    num_days = int(days)
                    main_event_day = min(2, (num_days + 1) // 2) if num_days > 1 else 1
                except:
                    main_event_day = 1
            else:
                # Fallback for when no event details are provided
                event_title = "Local Event"
                event_date = ""
                event_venue = ""
                event_description = "Special local event"
                main_event_day = 1
            
            # Get AI recommendations
            response = self.chain.invoke({
                "destination": destination,
                "days": days,
                "event_title": event_title,
                "event_date": event_date,
                "event_venue": event_venue,
                "event_description": event_description,
                "main_event_day": main_event_day
            })
            raw_json = response.content.strip()
            
            # Clean up common JSON issues
            if raw_json.startswith('```json'):
                raw_json = raw_json[7:]
            if raw_json.endswith('```'):
                raw_json = raw_json[:-3]
            
            itinerary = json.loads(raw_json)
            
            # Validate response
            if self._validate_json(itinerary):
                # Cache the result
                self.cache[cache_key] = {
                    'data': itinerary,
                    'timestamp': time.time()
                }
                return itinerary
            else:
                raise ValueError("Invalid itinerary format returned")
                
        except Exception as e:
            print(f"Itinerary Agent Error: {e}")
            # Return fallback data
            fallback = self._get_fallback_data(destination, days, event_details)
            self.cache[cache_key] = {
                'data': fallback,
                'timestamp': time.time()
            }
            return fallback

# Example usage
if __name__ == "__main__":
    agent = ItineraryAgent()
    result = agent.generate_itinerary("Toronto", "3")
    print(json.dumps(result, indent=2))
