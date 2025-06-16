from typing import Dict, Any
from agents.base_agent import BaseAgent
from models.trip_models import Destination

class DestinationAgent(BaseAgent):
    """Agent specialized in suggesting travel destinations"""
    
    def __init__(self):
        super().__init__("Destination Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest destinations based on user preferences"""
        
        preferences = input_data.get("preferences", [])
        budget = input_data.get("budget", "medium")
        travelers = input_data.get("travelers", 1)
        existing_destination = input_data.get("destination")
        
        if existing_destination:
            # If destination is already specified, provide information about it
            system_prompt = """You are a destination expert. Provide detailed information about the given destination including best time to visit and budget estimates."""
            user_prompt = f"Provide information about {existing_destination} for {travelers} travelers with a {budget} budget."
        else:
            # Suggest destinations based on preferences
            system_prompt = """You are a travel destination expert. Suggest the best travel destinations based on user preferences and budget. Focus on providing practical and popular destinations."""
            
            prefs_str = ", ".join(preferences) if preferences else "general travel"
            user_prompt = f"Suggest 3 great destinations for {travelers} travelers who enjoy {prefs_str} with a {budget} budget. Include brief descriptions."
        
        response = self._make_llm_call(system_prompt, user_prompt)
        
        return {
            "agent": self.name,
            "suggestions": response,
            "status": "completed"
        }
