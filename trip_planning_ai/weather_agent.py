from langchain_core.tools import tool
import requests

@tool
def get_weather(destination: str) -> str:
    """Fetch current weather for a city (no API key required). Returns temperature and wind info."""
    try:
        # Step 1: Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=1"
        geo_resp = requests.get(geo_url)
        geo_data = geo_resp.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"Could not find location: {destination}"

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # Step 2: Get current weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_resp = requests.get(weather_url)
        weather_data = weather_resp.json()

        current = weather_data.get("current_weather", {})
        if not current:
            return "Weather data unavailable."

        return f"Weather in {destination}: {current['temperature']}°C with wind speed of {current['windspeed']} km/h."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

