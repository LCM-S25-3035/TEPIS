"""
Transportation Agent for travel and local transportation recommendations
"""

import os
import json
import time
import hashlib
import requests
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
        
        # Google Maps API key - hardcoded as requested
        self.google_maps_api_key = "AIzaSyDriqtz6KB-2pSbCQ0zFNmwi5ZrhGZeDqM"

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
    
    def get_home_to_destination_routes(self, user_address, destination_address):
        """Get actual routes from user address to event destination using Google Maps API"""
        if not user_address or not destination_address:
            return None
        
        cache_key = hashlib.md5(f"{user_address.lower()}_{destination_address.lower()}".encode()).hexdigest()
        
        # Check cache first (1 hour validity for route data)
        if cache_key in self.cache:
            cached_entry = self.cache[cache_key]
            if cached_entry and time.time() - cached_entry.get('timestamp', 0) < 3600:  # 1 hour
                return cached_entry['data']
        
        try:
            routes_data = {
                "user_address": user_address,
                "destination": destination_address,
                "routes": [],
                "distance_km": 0,
                "flight_required": False
            }
            
            # Transportation modes to check
            modes = [
                {"mode": "driving", "name": "🚗 Driving", "icon": "🚗"},
                {"mode": "transit", "name": "🚌 Public Transit", "icon": "🚌"},
                {"mode": "walking", "name": "🚶 Walking", "icon": "🚶"}
            ]
            
            base_url = "https://maps.googleapis.com/maps/api/directions/json"
            
            # First, get driving route to determine distance
            driving_params = {
                "origin": user_address,
                "destination": destination_address,
                "mode": "driving",
                "key": self.google_maps_api_key
            }
            
            driving_response = requests.get(base_url, params=driving_params, timeout=10)
            driving_data = driving_response.json()
            
            if driving_data.get("status") == "OK" and driving_data.get("routes"):
                route = driving_data["routes"][0]
                leg = route["legs"][0]
                distance_km = leg["distance"]["value"] / 1000  # Convert meters to km
                routes_data["distance_km"] = distance_km
                
                # If distance > 500km, suggest flying
                if distance_km > 500:
                    routes_data["flight_required"] = True
                    routes_data["routes"].append({
                        "mode": "flight",
                        "name": "✈️ Flight",
                        "icon": "✈️",
                        "duration": "2-4 hours",
                        "distance": f"{distance_km:.0f} km",
                        "cost_estimate": f"${distance_km * 0.15:.0f}-${distance_km * 0.3:.0f}",
                        "description": "Recommended for long distances",
                        "steps": ["Book flight from nearest airport", "Airport transfer on both ends"]
                    })
            
            # Get routes for each transportation mode
            for mode_info in modes:
                try:
                    params = {
                        "origin": user_address,
                        "destination": destination_address,
                        "mode": mode_info["mode"],
                        "key": self.google_maps_api_key
                    }
                    
                    response = requests.get(base_url, params=params, timeout=10)
                    data = response.json()
                    
                    if data.get("status") == "OK" and data.get("routes"):
                        route = data["routes"][0]
                        leg = route["legs"][0]
                        
                        # Calculate estimated cost
                        distance_km = leg["distance"]["value"] / 1000
                        duration_text = leg["duration"]["text"]
                        
                        cost_estimate = "N/A"
                        if mode_info["mode"] == "driving":
                            gas_cost = distance_km * 0.12  # Estimate $0.12 per km
                            cost_estimate = f"${gas_cost:.2f} (gas)"
                        elif mode_info["mode"] == "transit":
                            cost_estimate = "$3-15 (fare)"
                        elif mode_info["mode"] == "walking":
                            cost_estimate = "Free"
                        
                        # Extract key steps
                        steps = []
                        for step in route["legs"][0]["steps"][:3]:  # First 3 steps
                            instruction = step["html_instructions"]
                            # Clean HTML tags
                            import re
                            clean_instruction = re.sub('<[^<]+?>', '', instruction)
                            steps.append(clean_instruction)
                        
                        routes_data["routes"].append({
                            "mode": mode_info["mode"],
                            "name": mode_info["name"],
                            "icon": mode_info["icon"],
                            "duration": duration_text,
                            "distance": leg["distance"]["text"],
                            "cost_estimate": cost_estimate,
                            "description": f"{mode_info['name']} route via {route['summary'] if 'summary' in route else 'main roads'}",
                            "steps": steps
                        })
                
                except Exception as mode_error:
                    print(f"Error getting {mode_info['mode']} route: {mode_error}")
                    continue
            
            # Cache the result
            self.cache[cache_key] = {
                'data': routes_data,
                'timestamp': time.time()
            }
            
            return routes_data
            
        except Exception as e:
            print(f"Google Maps API Error: {e}")
            # Return fallback data
            return {
                "user_address": user_address,
                "destination": destination_address,
                "routes": [
                    {
                        "mode": "driving",
                        "name": "🚗 Driving",
                        "icon": "🚗",
                        "duration": "Calculating...",
                        "distance": "Unknown",
                        "cost_estimate": "Varies",
                        "description": "Route calculation unavailable",
                        "steps": ["Please check Google Maps for directions"]
                    }
                ],
                "distance_km": 0,
                "flight_required": False,
                "error": "Unable to calculate routes at this time"
            }

# Example usage
if __name__ == "__main__":
    agent = TransportationAgent()
    result = agent.get_recommendations("Toronto")
    print(json.dumps(result, indent=2))
