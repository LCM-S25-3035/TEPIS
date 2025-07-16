"""
Weather Agent for getting current weather information
"""

import requests
import json
import time
import hashlib

class WeatherAgent:
    def __init__(self):
        # Cache for responses
        self.cache = {}
        
    def _get_cache_key(self, destination):
        """Generate cache key for destination"""
        return hashlib.md5(f"weather_{destination}".lower().encode()).hexdigest()

    def _is_cache_valid(self, cache_entry):
        """Check if cache entry is still valid (1 hour for weather)"""
        if not cache_entry:
            return False
        
        cached_time = cache_entry.get('timestamp', 0)
        return time.time() - cached_time < 3600  # 1 hour

    def _get_coordinates(self, destination):
        """Get latitude and longitude from destination name"""
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=1"
            geo_resp = requests.get(geo_url, timeout=10)
            geo_data = geo_resp.json()

            if "results" not in geo_data or not geo_data["results"]:
                raise ValueError(f"Could not find location: {destination}")

            location = geo_data["results"][0]
            return {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "name": location.get("name", destination),
                "country": location.get("country", "Unknown")
            }
        except Exception as e:
            print(f"Geocoding Error: {e}")
            return None

    def _get_weather_data(self, lat, lon):
        """Get weather data from Open-Meteo API"""
        try:
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&current_weather=true&"
                f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
                f"timezone=auto"
            )
            
            weather_resp = requests.get(weather_url, timeout=10)
            weather_data = weather_resp.json()

            current = weather_data.get("current_weather", {})
            if not current:
                raise ValueError("No weather data available")

            # Get weather condition description
            weather_code = current.get("weathercode", 0)
            condition = self._get_weather_condition(weather_code)

            return {
                "temperature_celsius": current["temperature"],
                "windspeed_kph": current["windspeed"],
                "condition": condition,
                "description": f"{current['temperature']}°C, {condition}",
                "is_day": current.get("is_day", 1) == 1
            }
        except Exception as e:
            print(f"Weather API Error: {e}")
            return None

    def _get_weather_condition(self, weather_code):
        """Convert weather code to readable condition"""
        conditions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Drizzle: Light",
            53: "Drizzle: Moderate",
            55: "Drizzle: Dense",
            61: "Rain: Slight",
            63: "Rain: Moderate",
            65: "Rain: Heavy",
            80: "Rain showers: Slight",
            81: "Rain showers: Moderate",
            82: "Rain showers: Violent",
            95: "Thunderstorm: Slight",
            96: "Thunderstorm with hail"
        }
        return conditions.get(weather_code, "Unknown")

    def _get_fallback_data(self, destination):
        """Fallback data if API fails"""
        return {
            "temperature_celsius": 20,
            "windspeed_kph": 10,
            "condition": "Partly cloudy",
            "description": f"Weather data temporarily unavailable for {destination}",
            "is_day": True,
            "location": {
                "name": destination,
                "country": "Unknown"
            }
        }

    def get_weather(self, destination):
        """Get weather for destination"""
        cache_key = self._get_cache_key(destination)
        
        # Check cache first
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']
        
        # Get coordinates
        coordinates = self._get_coordinates(destination)
        if not coordinates:
            fallback = self._get_fallback_data(destination)
            self.cache[cache_key] = {
                'data': fallback,
                'timestamp': time.time()
            }
            return fallback
        
        # Get weather data
        weather_data = self._get_weather_data(
            coordinates["latitude"], 
            coordinates["longitude"]
        )
        
        if not weather_data:
            fallback = self._get_fallback_data(destination)
            self.cache[cache_key] = {
                'data': fallback,
                'timestamp': time.time()
            }
            return fallback
        
        # Add location info to weather data
        weather_data["location"] = {
            "name": coordinates["name"],
            "country": coordinates["country"]
        }
        
        # Cache the result
        self.cache[cache_key] = {
            'data': weather_data,
            'timestamp': time.time()
        }
        
        return weather_data

# Example usage
if __name__ == "__main__":
    agent = WeatherAgent()
    result = agent.get_weather("Toronto")
    print(json.dumps(result, indent=2))
