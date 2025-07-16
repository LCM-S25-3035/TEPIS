"""
Restaurant Agent for event-specific restaurant recommendations
"""

import os
import json
import time
import hashlib
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

class RestaurantAgent:
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
List 5 top-rated restaurants in {destination} suitable for event attendees.
Return ONLY JSON in this exact format:

{{
  "restaurants": [
    {{
      "name": "Restaurant Name",
      "cuisine": "Cuisine Type",
      "description": "Short description of the restaurant",
      "rating": 4.7,
      "price_range": "$$",
      "address": "Street Address or Area",
      "features": ["Outdoor Seating", "Vegetarian Options", "Reservations"],
      "website": "https://restaurant.com"
    }}
  ]
}}

Only return valid JSON, no additional text.
""")
        
        self.chain = self.prompt_template | self.llm

    def _get_cache_key(self, destination):
        """Generate cache key for destination"""
        return hashlib.md5(f"restaurants_{destination}".lower().encode()).hexdigest()

    def _is_cache_valid(self, cache_entry):
        """Check if cache entry is still valid (24 hours)"""
        if not cache_entry:
            return False
        
        cached_time = cache_entry.get('timestamp', 0)
        return time.time() - cached_time < 86400  # 24 hours

    def _validate_json(self, data):
        """Validate restaurant JSON structure"""
        if not isinstance(data, dict):
            return False
        
        if 'restaurants' not in data:
            return False
        
        if not isinstance(data['restaurants'], list):
            return False
        
        for restaurant in data['restaurants']:
            required_fields = ['name', 'cuisine', 'description', 'rating', 'price_range', 'address']
            if not all(field in restaurant for field in required_fields):
                return False
        
        return True

    def _get_fallback_data(self, destination):
        """Fallback data if AI fails"""
        return {
            "restaurants": [
                {
                    "name": f"The Local Bistro {destination}",
                    "cuisine": "International",
                    "description": "Popular local restaurant with diverse menu",
                    "rating": 4.5,
                    "price_range": "$$",
                    "address": f"Downtown {destination}",
                    "features": ["Outdoor Seating", "Vegetarian Options", "Reservations"],
                    "website": "https://restaurant.com"
                },
                {
                    "name": f"Fine Dining {destination}",
                    "cuisine": "Contemporary",
                    "description": "Upscale restaurant perfect for business dinners",
                    "rating": 4.7,
                    "price_range": "$$$",
                    "address": f"Business District {destination}",
                    "features": ["Private Dining", "Wine List", "Reservations Required"],
                    "website": "https://restaurant.com"
                },
                {
                    "name": f"Casual Eats {destination}",
                    "cuisine": "Comfort Food",
                    "description": "Relaxed atmosphere with comfort food favorites",
                    "rating": 4.2,
                    "price_range": "$",
                    "address": f"Central {destination}",
                    "features": ["Quick Service", "Takeout", "Family Friendly"],
                    "website": "https://restaurant.com"
                },
                {
                    "name": f"Ethnic Kitchen {destination}",
                    "cuisine": "Asian Fusion",
                    "description": "Authentic flavors with modern presentation",
                    "rating": 4.4,
                    "price_range": "$$",
                    "address": f"Cultural District {destination}",
                    "features": ["Authentic Cuisine", "Vegetarian Options", "Delivery"],
                    "website": "https://restaurant.com"
                },
                {
                    "name": f"Café Corner {destination}",
                    "cuisine": "Café",
                    "description": "Perfect for quick breakfast or coffee meetings",
                    "rating": 4.0,
                    "price_range": "$",
                    "address": f"City Center {destination}",
                    "features": ["Coffee", "WiFi", "Breakfast", "Pastries"],
                    "website": "https://restaurant.com"
                }
            ]
        }

    def get_recommendations(self, destination):
        """Get restaurant recommendations for destination"""
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
            
            restaurants = json.loads(raw_json)
            
            # Validate response
            if self._validate_json(restaurants):
                # Cache the result
                self.cache[cache_key] = {
                    'data': restaurants,
                    'timestamp': time.time()
                }
                return restaurants
            else:
                raise ValueError("Invalid restaurant format returned")
                
        except Exception as e:
            print(f"Restaurant Agent Error: {e}")
            # Return fallback data
            fallback = self._get_fallback_data(destination)
            self.cache[cache_key] = {
                'data': fallback,
                'timestamp': time.time()
            }
            return fallback

# Example usage
if __name__ == "__main__":
    agent = RestaurantAgent()
    result = agent.get_recommendations("Toronto")
    print(json.dumps(result, indent=2))
