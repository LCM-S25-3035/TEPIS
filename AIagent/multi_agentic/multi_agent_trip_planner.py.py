# multi_agent_trip_planner.py
"""
Skeleton for a multi-agent trip planning framework using LangChain-style tools
"""
from typing import Dict, Any, List

# ---------- Base Agent ----------
class Agent:
    def __init__(self, name: str):
        self.name = name

    def run(self, context: Dict[str, Any]) -> None:
        """Process the shared TripContext in-place"""
        raise NotImplementedError("Agent must implement run()")

# ---------- Trip Context ----------
class TripContext(dict):
    """Holds all shared data between agents"""
    pass

# ---------- Sample Agents ----------
class EventAgent(Agent):
    def __init__(self):
        super().__init__("EventAgent")

    def run(self, context: TripContext) -> None:
        # Fetch event details from database (pseudo-code)
        event_id = context.get("event_id")
        # Example: query MongoDB
        # event = db.events.find_one({"_id": event_id})
        event = {
            "name": "Music Fest",
            "location": {"lat": 43.5907, "lng": -79.6436},
            "date": "2025-07-15",
            "start_time": "18:00"
        }
        context["event"] = event
        print(f"[{self.name}] loaded event: {event['name']}")

# ---------- Example Usage ----------
def main():
    agents = [EventAgent()]

    user_input = {
        "event_id": "evt123",
        "user_location": {"lat": 43.6532, "lng": -79.3832},
        "budget": 300,
        "days": 2
    }
    print("--- Final Trip Context ---")


if __name__ == "__main__":
    main()
