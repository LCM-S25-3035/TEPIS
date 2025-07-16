"""
Hotel Agent for event-specific hotel recommendations
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

class HotelAgent:
    def __init__(self, api_token=None):
        # Set API token from parameter or use fallback for testing
        if api_token:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_token
        
        # Initialize model
        self.endpoint = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            task="text-generation",
            max_new_tokens=512,
            temperature=0.7
        )
        self.llm = ChatHuggingFace(llm=self.endpoint)
        
        # Cache for responses
        self.cache = {}
        
        # Prompt template
        self.prompt_template = PromptTemplate.from_template("""
Generate a list of 5 hotels in {destination} suitable for event attendees.
Return ONLY JSON in this exact format:

{{
  "hotels": [
    {{
      "name": "Hotel Name",
      "description": "Brief description of the hotel",
      "rating": 4.5,
      "price_category": "Luxury",
      "location": "Hotel address or neighborhood",
      "amenities": ["Free WiFi", "Spa", "Gym"],
      "booking_url": "https://booking.com"
    }}
  ]
}}

Only return valid JSON, no additional text.
""")
        
        self.chain = self.prompt_template | self.llm

    def _get_cache_key(self, destination):
        """Generate cache key for destination"""
        return hashlib.md5(destination.lower().encode()).hexdigest()

    def _is_cache_valid(self, cache_entry):
        """Check if cache entry is still valid (24 hours)"""
        if not cache_entry:
            return False
        
        cached_time = cache_entry.get('timestamp', 0)
        return time.time() - cached_time < 86400  # 24 hours

    def _validate_json(self, data):
        """Validate hotel JSON structure"""
        if not isinstance(data, dict):
            return False
        
        if 'hotels' not in data:
            return False
        
        if not isinstance(data['hotels'], list):
            return False
        
        for hotel in data['hotels']:
            required_fields = ['name', 'description', 'rating', 'price_category', 'location']
            if not all(field in hotel for field in required_fields):
                return False
        
        return True

    def _get_fallback_data(self, destination):
        """Fallback data if AI fails"""
        return {
            "hotels": [
                {
                    "name": f"Grand Hotel {destination}",
                    "description": "Luxury hotel in the heart of the city",
                    "rating": 4.5,
                    "price_category": "Luxury",
                    "location": f"Downtown {destination}",
                    "amenities": ["Free WiFi", "Spa", "Gym", "Business Center"],
                    "booking_url": "https://booking.com"
                },
                {
                    "name": f"Business Inn {destination}",
                    "description": "Modern hotel perfect for business travelers",
                    "rating": 4.0,
                    "price_category": "Business",
                    "location": f"Business District {destination}",
                    "amenities": ["Free WiFi", "Meeting Rooms", "Gym"],
                    "booking_url": "https://booking.com"
                },
                {
                    "name": f"Comfort Stay {destination}",
                    "description": "Affordable comfort in a great location",
                    "rating": 3.8,
                    "price_category": "Moderate",
                    "location": f"Central {destination}",
                    "amenities": ["Free WiFi", "Breakfast", "Parking"],
                    "booking_url": "https://booking.com"
                }
            ]
        }

    def get_recommendations(self, destination):
        """Get hotel recommendations for destination"""
        cache_key = self._get_cache_key(destination)
        
        # Check cache first
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']
        
        try:
            # Get AI recommendations
            response = self.chain.invoke({"destination": destination})
            raw_json = response.content.strip()
            
            # Clean up common JSON issues
            if raw_json.startswith('```json'):
                raw_json = raw_json[7:]
            if raw_json.endswith('```'):
                raw_json = raw_json[:-3]
            
            hotels = json.loads(raw_json)
            
            # Validate response
            if self._validate_json(hotels):
                # Cache the result
                self.cache[cache_key] = {
                    'data': hotels,
                    'timestamp': time.time()
                }
                return hotels
            else:
                raise ValueError("Invalid hotel format returned")
                
        except Exception as e:
            print(f"Hotel Agent Error: {e}")
            # Return fallback data
            fallback = self._get_fallback_data(destination)
            self.cache[cache_key] = {
                'data': fallback,
                'timestamp': time.time()
            }
            return fallback

# Example usage
if __name__ == "__main__":
    agent = HotelAgent()
    result = agent.get_recommendations("Toronto")
    print(json.dumps(result, indent=2))
