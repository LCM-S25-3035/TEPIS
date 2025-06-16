import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator_agent import CoordinatorAgent

load_dotenv()

def get_user_input():
    """Get trip planning input from user via terminal"""
    print("=" * 50)
    print("Welcome to AI Trip Planning System!")
    print("=" * 50)
    
    destination = input("Enter destination: ").strip()
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    try:
        budget = float(input("Enter budget ($): ").strip())
    except ValueError:
        budget = 1000.0
        print("Invalid budget, using default $1000")
    
    try:
        travelers = int(input("Number of travelers: ").strip())
    except ValueError:
        travelers = 1
        print("Invalid number, using default 1 traveler")
    
    print("\nPreferences (enter comma-separated, or press Enter to skip):")
    print("Examples: adventure, culture, food, nature, history, nightlife")
    preferences_input = input("Preferences: ").strip()
    preferences = [p.strip() for p in preferences_input.split(',')] if preferences_input else []
    
    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "travelers": travelers,
        "preferences": preferences
    }

def display_trip_plan(result):
    """Display the trip plan in a formatted way"""
    print("\n" + "=" * 60)
    print("YOUR PERSONALIZED TRIP PLAN")
    print("=" * 60)
    
    # Display main trip plan
    if result.get("trip_plan"):
        print(f"\n📋 TRIP OVERVIEW:")
        print(result["trip_plan"])
    
    # Display individual agent results
    details = result.get("individual_results", {})
    
    if details.get("destination"):
        print(f"\n📍 DESTINATION INFO:")
        print(details["destination"])
    
    if details.get("weather"):
        print(f"\n🌤️  WEATHER FORECAST:")
        print(details["weather"])
    
    if details.get("accommodation"):
        print(f"\n🏨 ACCOMMODATION SUGGESTIONS:")
        print(details["accommodation"])
    
    if details.get("activity"):
        print(f"\n🎯 ACTIVITY RECOMMENDATIONS:")
        print(details["activity"])
    
    print("\n" + "=" * 60)
    print("Have a wonderful trip! 🌟")
    print("=" * 60)

def main():
    """Main application loop"""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key as an environment variable.")
        return
    
    while True:
        try:
            # Get user input
            trip_request = get_user_input()
            
            print("\n🤖 Planning your trip with AI agents...")
            print("This may take a moment...\n")
            
            # Create coordinator and plan trip
            coordinator = CoordinatorAgent()
            result = coordinator.process(trip_request)
            
            # Display results
            display_trip_plan(result)
            
            # Ask if user wants to plan another trip
            print("\nWould you like to plan another trip? (y/n): ", end="")
            if input().lower().strip() not in ['y', 'yes']:
                break
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! Thanks for using AI Trip Planning System!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")

if __name__ == '__main__':
    main()
