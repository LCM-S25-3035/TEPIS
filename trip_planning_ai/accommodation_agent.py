from typing import Dict, Any
from agents.base_agent import BaseAgent

class AccommodationAgent(BaseAgent):
    """Agent specialized in finding accommodations"""
    
    def __init__(self):
        super().__init__("Accommodation Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find suitable accommodations"""
        
        destination = input_data.get("destination", "the destination")
        budget = input_data.get("budget", "medium")
        travelers = input_data.get("travelers", 1)
        start_date = input_data.get("start_date", "")
        end_date = input_data.get("end_date", "")
        
        system_prompt = """You are an accommodation expert. Recommend suitable hotels, hostels, or other lodging options based on destination, budget, and group size. Provide specific recommendations with estimated prices."""
        
        user_prompt = f"""Find accommodations in {destination} for {travelers} travelers from {start_date} to {end_date} with a {budget} budget. 
        Suggest 3 different options (like hotel, hostel, Airbnb) with approximate prices and key amenities."""
        
        response = self._make_llm_call(system_prompt, user_prompt)
        
        return {
            "agent": self.name,
            "accommodations": response,
            "status": "completed"
        }
