from typing import Dict, Any, List
from datetime import datetime
import re

def get_user_input() -> Dict[str, Any]:
    """Collect user input for trip planning"""
    
    print("🌟 Welcome to the AI Trip Planning System! 🌟")
    print("Let's plan your perfect trip together!\n")
    
    # Get destination
    destination = input("Enter your destination (or press Enter to get suggestions): ").strip()
    if not destination:
        destination = None
    
    # Get travel dates
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    # Get number of travelers
    while True:
        try:
            travelers = int(input("Number of travelers: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Get budget
    print("\nBudget options:")
    print("1. Low budget (backpacker/budget traveler)")
    print("2. Medium budget (comfortable mid-range)")
    print("3. High budget (luxury travel)")
    
    budget_map = {"1": "low", "2": "medium", "3": "high"}
    while True:
        budget_choice = input("Select budget (1-3): ").strip()
        if budget_choice in budget_map:
            budget = budget_map[budget_choice]
            break
        print("Please enter 1, 2, or 3.")
    
    # Get preferences
    print("\nTravel preferences (enter numbers separated by commas):")
    print("1. Beach/Ocean  2. Mountains  3. Culture/History  4. Adventure")
    print("5. Food/Cuisine  6. Nightlife  7. Nature/Wildlife  8. Art/Museums")
    print("9. Shopping  10. Relaxation/Spa")
    
    preference_map = {
        "1": "beach", "2": "mountains", "3": "culture", "4": "adventure",
        "5": "food", "6": "nightlife", "7": "nature", "8": "art",
        "9": "shopping", "10": "relaxation"
    }
    
    pref_input = input("Enter your preferences (e.g., 1,3,5): ").strip()
    preferences = []
    if pref_input:
        for p in pref_input.split(","):
            p = p.strip()
            if p in preference_map:
                preferences.append(preference_map[p])
    
    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "budget": budget,
        "preferences": preferences
    }

def validate_dates(start_date: str, end_date: str) -> bool:
    """Validate date format and logical order"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return start <= end
    except ValueError:
        return False

def print_trip_plan(result: Dict[str, Any]) -> None:
    """Pretty print the trip plan result"""
    
    print("\n" + "="*60)
    print("🎉 YOUR PERSONALIZED TRIP PLAN 🎉")
    print("="*60)
    
    if result.get("status") == "completed":
        trip_plan = result.get("trip_plan", "")
        print(trip_plan)
        
        print("\n" + "-"*40)
        print("📋 DETAILED BREAKDOWN")
        print("-"*40)
        
        individual = result.get("individual_results", {})
        
        if "destinations" in individual:
            print("\n🌍 DESTINATION INFO:")
            print(individual["destinations"].get("suggestions", ""))
        
        if "accommodations" in individual:
            print("\n🏨 ACCOMMODATION OPTIONS:")
            print(individual["accommodations"].get("accommodations", ""))
        
        if "activities" in individual:
            print("\n🎯 ACTIVITIES & ATTRACTIONS:")
            print(individual["activities"].get("activities", ""))
        
        if "weather" in individual:
            print("\n🌤️ WEATHER INFORMATION:")
            print(individual["weather"].get("weather_info", ""))
    
    else:
        print("❌ There was an error creating your trip plan.")
        print("Please check your API key and try again.")
    
    print("\n" + "="*60)
    print("Thank you for using the AI Trip Planning System! ✈️")
    print("="*60)
