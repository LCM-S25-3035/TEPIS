from typing import Dict, Any
from agents.base_agent import BaseAgent
import requests
import os

class WeatherAgent(BaseAgent):
    """Agent specialized in providing weather information"""
    
    def __init__(self):
        super().__init__("Weather Agent")
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide weather information and recommendations"""
        
        destination = input_data.get("destination", "the destination")
        start_date = input_data.get("start_date", "")
        end_date = input_data.get("end_date", "")
        
        # For this basic version, we'll use LLM for weather info
        # In production, you'd integrate with a real weather API
        system_prompt = """You are a weather expert. Provide general weather information for destinations during specific time periods, including what to pack and weather-related recommendations."""
        
        user_prompt = f"""Provide weather information and recommendations for {destination} from {start_date} to {end_date}. 
        Include:
        - Expected weather conditions
        - Temperature ranges
        - What to pack
        - Weather-related activity recommendations
        - Any seasonal considerations"""
        
        response = self._make_llm_call(system_prompt, user_prompt)
        
        return {
            "agent": self.name,
            "weather_info": response,
            "status": "completed"
        }
