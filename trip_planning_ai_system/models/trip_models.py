from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class TripRequest(BaseModel):
    """Model for trip planning request"""
    destination: str
    start_date: datetime
    end_date: datetime
    budget: Optional[float] = None
    interests: List[str] = []
    group_size: int = 1
    accommodation_type: Optional[str] = None
    transportation_preference: Optional[str] = None

class Event(BaseModel):
    """Model for events"""
    name: str
    description: str
    location: str
    date: datetime
    price: Optional[float] = None
    category: str
    rating: Optional[float] = None

class Accommodation(BaseModel):
    """Model for accommodations"""
    name: str
    location: str
    price_per_night: float
    rating: float
    amenities: List[str] = []
    check_in: datetime
    check_out: datetime

class Transportation(BaseModel):
    """Model for transportation options"""
    mode: str  # flight, train, car, bus
    departure_location: str
    arrival_location: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    provider: str

class TripPlan(BaseModel):
    """Complete trip plan model"""
    destination: str
    duration_days: int
    total_budget: float
    accommodations: List[Accommodation]
    transportation: List[Transportation]
    events: List[Event]
    daily_itinerary: Dict[str, List[Dict]]
    recommendations: List[str]
