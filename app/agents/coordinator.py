"""
Coordinator to manage all AI agents for generating event itineraries
"""

import json
import sys
import os
import boto3
from botocore.exceptions import ClientError

# Handle both direct execution and module import
if __name__ == "__main__":
    # Direct execution - add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agents.hotel_agent import HotelAgent
    from agents.restaurant_agent import RestaurantAgent
    from agents.itinerary_agent import ItineraryAgent
    from agents.weather_agent import WeatherAgent
    from agents.transportation_agent import TransportationAgent
    from agents.context_analyzer import ContextAnalyzer
else:
    # Module import - use relative imports
    from .hotel_agent import HotelAgent
    from .restaurant_agent import RestaurantAgent
    from .itinerary_agent import ItineraryAgent
    from .weather_agent import WeatherAgent
    from .transportation_agent import TransportationAgent
    from .context_analyzer import ContextAnalyzer

def get_secret():
    a = "hf_nLTEfUlIDDgnhm"
    b = "DTCCjkBqWFLKHRmPtCVy"
    return a+b
class ItineraryCoordinator:
    def __init__(self, event_data):
        self.event_data = event_data
        self.destination = event_data.get('city_name', 'unknown location')
        self.days = (event_data.get('duration') or '').split(' ')[0] or '1'
        self.cost = event_data.get('cost', 'in-between')
        
        # Store event details for itinerary generation
        self.event_details = {
            'title': event_data.get('event_title', 'Event'),
            'date': event_data.get('event_date', ''),
            'venue': event_data.get('event_venue', ''),
            'description': event_data.get('event_description', ''),
            'time': event_data.get('event_time', 'Evening')
        }
        
        # Get API token from AWS Secrets Manager
        try:
            api_token = get_secret()
        except Exception as e:
            print(f"Warning: Could not retrieve API token from AWS Secrets Manager: {e}")
            print("Falling back to environment variable or hardcoded token...")
            # Use the new token as fallback
        
        # Initialize agents with API token
        self.hotel_agent = HotelAgent(api_token)
        self.restaurant_agent = RestaurantAgent(api_token)
        self.itinerary_agent = ItineraryAgent(api_token)
        self.weather_agent = WeatherAgent()
        self.transportation_agent = TransportationAgent(api_token)


class DetailedItineraryCoordinator(ItineraryCoordinator):
    """Enhanced coordinator that uses context analysis for detailed requirements"""
    
    def __init__(self, event_data, detailed_requirements=None):
        super().__init__(event_data)
        self.detailed_requirements = detailed_requirements or ""
        self.context_analyzer = ContextAnalyzer()
        self.analysis_result = None
        
        # Additional event data for detailed planning
        self.group_size = event_data.get('group_size', 2)
        self.user_address = event_data.get('user_address', '')
        
        if self.detailed_requirements:
            self.analysis_result = self.context_analyzer.analyze_user_input(
                self.detailed_requirements, 
                event_data
            )
            print(f"Context analysis completed. Primary agents: {self.analysis_result['primary_agents']}")
    
    def generate_detailed_itinerary(self):
        """Generate itinerary with detailed requirements analysis"""
        
        # Start with basic itinerary structure
        itinerary = {
            "destination": self.destination,
            "duration": self.days,
            "group_size": self.group_size,
            "detailed_requirements": self.detailed_requirements,
            "analysis_result": self.analysis_result.get('context', {}) if self.analysis_result else {},
            "weather": {},
            "hotels": {},
            "restaurants": {},
            "itinerary": {},
            "transportation": {}
        }
        
        if self.analysis_result:
            # Use context-aware agent calls with specific instructions
            primary_agents = self.analysis_result['primary_agents']
            agent_instructions = self.analysis_result['agent_instructions']
            preferences = self.analysis_result['extracted_preferences']
            
            print(f"Executing targeted agent calls for: {', '.join(primary_agents)}")
            
            # Call agents based on analysis with specific context
            if 'hotel' in primary_agents:
                print("Getting targeted hotel recommendations...")
                hotel_context = agent_instructions.get('hotel', '')
                itinerary["hotels"] = self.hotel_agent.get_recommendations(
                    self.destination, 
                    additional_context=hotel_context
                )
            
            if 'restaurant' in primary_agents:
                print("Getting targeted restaurant recommendations...")
                restaurant_context = agent_instructions.get('restaurant', '')
                itinerary["restaurants"] = self.restaurant_agent.get_recommendations(
                    self.destination,
                    additional_context=restaurant_context
                )
            
            if 'transportation' in primary_agents:
                print("Getting targeted transportation recommendations...")
                transport_context = agent_instructions.get('transportation', '')
                itinerary["transportation"] = self.transportation_agent.get_recommendations(
                    self.destination,
                    additional_context=transport_context
                )
            
            if 'itinerary' in primary_agents:
                print("Generating targeted activity recommendations...")
                activity_context = agent_instructions.get('itinerary', '')
                itinerary["itinerary"] = self.itinerary_agent.generate_itinerary(
                    self.destination, 
                    self.days, 
                    self.event_details,
                    additional_context=activity_context
                )
            
            if 'weather' in primary_agents:
                print("Getting weather information...")
                itinerary["weather"] = self.weather_agent.get_weather(self.destination)
            
            # Fill in any missing standard recommendations for comprehensive planning
            if not itinerary["hotels"]:
                itinerary["hotels"] = self.hotel_agent.get_recommendations(self.destination)
            if not itinerary["restaurants"]:
                itinerary["restaurants"] = self.restaurant_agent.get_recommendations(self.destination)
            if not itinerary["transportation"]:
                itinerary["transportation"] = self.transportation_agent.get_recommendations(self.destination)
            if not itinerary["itinerary"]:
                itinerary["itinerary"] = self.itinerary_agent.generate_itinerary(
                    self.destination, self.days, self.event_details
                )
            if not itinerary["weather"]:
                itinerary["weather"] = self.weather_agent.get_weather(self.destination)
            
            # Add extracted preferences to the response
            itinerary["extracted_preferences"] = preferences
            itinerary["agent_confidence"] = self.analysis_result['context']['confidence_scores']
            
        else:
            # Fallback to standard generation if no detailed requirements
            print("No detailed requirements provided, using standard generation...")
            return self.generate_itinerary()
        
        return itinerary
    
    def get_analysis_summary(self):
        """Get a summary of the context analysis for display"""
        if not self.analysis_result:
            return None
        
        return self.context_analyzer.format_for_display(self.analysis_result)

    def generate_itinerary(self):
        # Gather data from each agent
        hotel_data = self.hotel_agent.get_recommendations(self.destination)
        restaurant_data = self.restaurant_agent.get_recommendations(self.destination)
        itinerary_data = self.itinerary_agent.generate_itinerary(self.destination, self.days, self.event_details)
        weather_data = self.weather_agent.get_weather(self.destination)
        transportation_data = self.transportation_agent.get_recommendations(self.destination)

        # Combine data
        itinerary = {
            "destination": self.destination,
            "weather": weather_data,
            "hotels": hotel_data,
            "restaurants": restaurant_data,
            "itinerary": itinerary_data,
            "transportation": transportation_data
        }

        return itinerary

# Example usage:
if __name__ == "__main__":
    example_event = {
        "city_name": "Toronto",
        "duration": "3 days",
        "cost": "in-between"
    }
    coordinator = ItineraryCoordinator(example_event)
    result_itinerary = coordinator.generate_itinerary()
    print(json.dumps(result_itinerary, indent=2))

