"""
Transportation Agent for travel and local transportation recommendations
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

class TransportationAgent:
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
Generate transportation recommendations for {destination} including flights, ground transportation, and local transit.
Return ONLY JSON in this exact format:

{{
  "transportation": {{
    "flights": {{
      "major_airports": ["Airport Name (CODE)", "Airport Name (CODE)"],
      "typical_flight_time": "X hours from major cities",
      "airlines": ["Airline 1", "Airline 2", "Airline 3"],
      "booking_tips": "Best booking advice"
    }},
    "ground_transportation": {{
      "from_airport": [
        {{
          "method": "Taxi",
          "duration": "30 minutes",
          "cost": "$40-60 CAD",
          "description": "Door-to-door service"
        }},
        {{
          "method": "Public Transit",
          "duration": "45 minutes",
          "cost": "$3-5 CAD",
          "description": "Airport express train/bus"
        }},
        {{
          "method": "Ride Share",
          "duration": "25-40 minutes",
          "cost": "$35-50 CAD",
          "description": "Uber/Lyft service"
        }}
      ],
      "car_rental": {{
        "available": true,
        "companies": ["Company 1", "Company 2", "Company 3"],
        "cost": "$50-80 CAD per day",
        "parking_info": "Downtown parking $20-30 CAD per day"
      }}
    }},
    "local_transit": {{
      "public_system": {{
        "name": "Transit System Name",
        "types": ["Subway", "Bus", "Streetcar"],
        "day_pass": "$12-15 CAD",
        "single_ride": "$3-4 CAD",
        "coverage": "Excellent city coverage"
      }},
      "walking": {{
        "walkability_score": 85,
        "description": "Very walkable downtown core"
      }},
      "bike_sharing": {{
        "available": true,
        "system_name": "Bike Share System",
        "cost": "$7-12 CAD per day"
      }}
    }}
  }}
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
        """Validate transportation JSON structure"""
        if not isinstance(data, dict):
            return False
        
        if 'transportation' not in data:
            return False
        
        transport = data['transportation']
        required_sections = ['flights', 'ground_transportation', 'local_transit']
        
        if not all(section in transport for section in required_sections):
            return False
        
        return True

    def _get_fallback_data(self, destination):
        """Fallback data if AI fails"""
        return {
            "transportation": {
                "flights": {
                    "major_airports": [f"{destination} International Airport"],
                    "typical_flight_time": "Varies by origin city",
                    "airlines": ["Major Airlines", "Regional Carriers"],
                    "booking_tips": "Book in advance for better rates"
                },
                "ground_transportation": {
                    "from_airport": [
                        {
                            "method": "Taxi",
                            "duration": "30-45 minutes",
                            "cost": "$40-70 CAD",
                            "description": "Door-to-door service"
                        },
                        {
                            "method": "Public Transit",
                            "duration": "45-60 minutes",
                            "cost": "$3-6 CAD",
                            "description": "Airport express service"
                        },
                        {
                            "method": "Ride Share",
                            "duration": "30-50 minutes",
                            "cost": "$35-55 CAD",
                            "description": "Uber/Lyft available"
                        }
                    ],
                    "car_rental": {
                        "available": True,
                        "companies": ["Enterprise", "Hertz", "Avis"],
                        "cost": "$50-90 CAD per day",
                        "parking_info": "Street parking and garages available"
                    }
                },
                "local_transit": {
                    "public_system": {
                        "name": f"{destination} Public Transit",
                        "types": ["Bus", "Train"],
                        "day_pass": "$10-15 CAD",
                        "single_ride": "$3-5 CAD",
                        "coverage": "Good city coverage"
                    },
                    "walking": {
                        "walkability_score": 70,
                        "description": "Moderately walkable city center"
                    },
                    "bike_sharing": {
                        "available": True,
                        "system_name": "City Bike Share",
                        "cost": "$8-15 CAD per day"
                    }
                }
            }
        }

    def get_recommendations(self, destination):
        """Get transportation recommendations for destination"""
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
            
            transportation = json.loads(raw_json)
            
            # Validate response
            if self._validate_json(transportation):
                # Cache the result
                self.cache[cache_key] = {
                    'data': transportation,
                    'timestamp': time.time()
                }
                return transportation
            else:
                raise ValueError("Invalid transportation format returned")
                
        except Exception as e:
            print(f"Transportation Agent Error: {e}")
            # Return fallback data
            fallback = self._get_fallback_data(destination)
            self.cache[cache_key] = {
                'data': fallback,
                'timestamp': time.time()
            }
            return fallback

# Example usage
if __name__ == "__main__":
    agent = TransportationAgent()
    result = agent.get_recommendations("Toronto")
    print(json.dumps(result, indent=2))
