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

class TransportAgent(Agent):
    def __init__(self):
        super().__init__("TransportAgent")

    def run(self, context: TripContext) -> None:
        from geopy.distance import geodesic
        # Fetch user location & event location
        user_loc = context.get("user_location", {"lat": 43.6532, "lng": -79.3832})
        event_loc = context["event"]["location"]
        # Calculate distance
        dist_km = geodesic((user_loc['lat'], user_loc['lng']), (event_loc['lat'], event_loc['lng'])).km
        # Simple logic: choose transport mode based on budget and distance
        budget = context.get("budget", 100)
        if dist_km < 50:
            mode = "Car"
            cost = dist_km * 0.2  # example $0.2 per km
        else:
            mode = "Train"
            cost = 50  # flat rate
        transport = {"mode": mode, "distance_km": dist_km, "cost": cost}
        context["transport"] = transport
        context["budget_remaining"] = budget - cost
        print(f"[{self.name}] transport: {mode}, cost: ${cost:.2f}")

class LodgingAgent(Agent):
    def __init__(self):
        super().__init__("LodgingAgent")

    def run(self, context: TripContext) -> None:
        # Fetch candidate hotels near event (pseudo)
        budget_rem = context.get("budget_remaining", 100)
        # Dummy list of hotels
        hotels = [
            {"name": "Budget Inn", "price_per_night": 50, "distance": 1.2},
            {"name": "Comfort Suites", "price_per_night": 120, "distance": 0.5},
            {"name": "Luxury Stay", "price_per_night": 200, "distance": 0.3}
        ]
        # Filter by price <= remaining budget / days
        days = context.get("days", 1)
        affordable = [h for h in hotels if h['price_per_night'] * days <= budget_rem]
        chosen = affordable[0] if affordable else hotels[0]
        lodging = {"hotel": chosen, "total_cost": chosen['price_per_night'] * days}
        context["lodging"] = lodging
        context["budget_remaining"] -= lodging['total_cost']
        print(f"[{self.name}] chosen hotel: {chosen['name']}")

class ActivitiesAgent(Agent):
    def __init__(self):
        super().__init__("ActivitiesAgent")

    def run(self, context: TripContext) -> None:
        # Suggest activities based on event location
        # Pseudo: call OpenTripMap or database
        activities = [
            {"name": "City Museum", "type": "museum", "duration_h": 2},
            {"name": "River Cruise", "type": "cruise", "duration_h": 1.5},
            {"name": "Local Market", "type": "shopping", "duration_h": 1}
        ]
        # Pick top-2 activities
        context["activities"] = activities[:2]
        print(f"[{self.name}] activities: {', '.join([a['name'] for a in activities[:2]])}")

# ---------- Orchestrator ----------
class TripPlanner:
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    def plan_trip(self, initial_context: Dict[str, Any]) -> TripContext:
        context = TripContext(initial_context)
        for agent in self.agents:
            agent.run(context)
        return context

# ---------- Example Usage ----------
def main():
    agents = [EventAgent(), TransportAgent(), LodgingAgent(), ActivitiesAgent()]
    planner = TripPlanner(agents)

    user_input = {
        "event_id": "evt123",
        "user_location": {"lat": 43.6532, "lng": -79.3832},
        "budget": 300,
        "days": 2
    }
    final_context = planner.plan_trip(user_input)
    print("--- Final Trip Context ---")
    for k, v in final_context.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
