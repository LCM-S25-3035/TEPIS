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
        
        # Prompt template
        self.prompt_template = PromptTemplate.from_template("""
Create a {days}-day itinerary for {destination} focusing on popular attractions and activities.
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
    "Top attraction 1",
    "Top attraction 2",
    "Top attraction 3"
  ],
  "trip_info": {{
    "duration": "{days} days",
    "category": "tourism",
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

    def _get_fallback_data(self, destination, days):
        """Fallback data if AI fails"""
        try:
            num_days = int(days)
        except:
            num_days = 1
        
        fallback_activities = []
        
        for day in range(1, num_days + 1):
            day_activities = {
                "day": day,
                "location": f"{destination} City Center",
                "activities": [
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
            }
            fallback_activities.append(day_activities)
        
        return {
            "itinerary": fallback_activities,
            "highlights": [
                f"Historic {destination} Downtown",
                f"{destination} Cultural District",
                f"Local {destination} Cuisine",
                f"{destination} Scenic Views"
            ],
            "trip_info": {
                "duration": f"{days} days",
                "category": "tourism",
                "price_range": "Moderate"
            }
        }

    def generate_itinerary(self, destination, days="1"):
        """Generate itinerary for destination and duration"""
        cache_key = self._get_cache_key(destination, days)
        
        # Check cache first
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']
        
        try:
            # Get AI recommendations
            response = self.chain.invoke({
                "destination": destination,
                "days": days
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
            fallback = self._get_fallback_data(destination, days)
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
