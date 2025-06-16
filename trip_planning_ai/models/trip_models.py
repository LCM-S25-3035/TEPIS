from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TripRequest(BaseModel):
    """User's trip planning request"""
    destination: Optional[str] = None
    budget: str  # "low", "medium", "high"
    start_date: str
    end_date: str
    travelers: int
    preferences: List[str]  # ["beach", "culture", "adventure", etc.]
    
class Destination(BaseModel):
    """Destination suggestion"""
    name: str
    country: str
    description: str
    best_time_to_visit: str
    estimated_budget: str
    
class Accommodation(BaseModel):
    """Hotel/lodging suggestion"""
    name: str
    type: str  # "hotel", "hostel", "airbnb"
    price_range: str
    location: str
    amenities: List[str]
    
class Activity(BaseModel):
    """Activity/attraction suggestion"""
    name: str
    type: str  # "sightseeing", "adventure", "cultural"
    duration: str
    cost: str
    description: str
    
class WeatherInfo(BaseModel):
    """Weather information"""
    location: str
    date: str
    temperature: str
    conditions: str
    recommendations: str
    
class TripPlan(BaseModel):
    """Complete trip plan"""
    destination: Destination
    accommodations: List[Accommodation]
    activities: List[Activity]
    weather_info: List[WeatherInfo]
    total_estimated_cost: str
    recommendations: List[str]
