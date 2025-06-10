import os
import json
from datetime import datetime
import openai

# 1. Set your API key (or load from env)
openai.api_key = os.getenv("OPENAI_API_KEY")  # export OPENAI_API_KEY="..."

# 2. Prepare your context data
event = {
    "name": "Music Fest",
    "date": "2025-07-15",
    "location": "Toronto, ON",
    "start_time": "18:00",
    "end_time": "23:00"
}

user_specs = {
    "budget": 300,
    "days": 2,
    "preferences": ["vegetarian", "no flights", "family-friendly"]
}

# 3. (Optional) fetch or pre-filter sub-options—e.g. hotels or attractions
# Here we just illustrate with a small hardcoded list
hotels = [
    {"name": "Budget Inn",   "price_per_night": 60,  "distance_km": 1.2},
    {"name": "Comfort Suites","price_per_night": 120, "distance_km": 0.5},
    {"name": "Luxury Stay",  "price_per_night": 200, "distance_km": 0.3},
]

# 4. Build your prompt
system_prompt = "You are a helpful trip-planning assistant."
user_prompt = f"""
A user has selected the following event:
{json.dumps(event, indent=2)}

And has provided these specifications:
{json.dumps(user_specs, indent=2)}

Available hotels:
{json.dumps(hotels, indent=2)}

Please create a {user_specs['days']}-day itinerary, including:
- Transportation to/from the event
- Hotel booking suggestion (with cost)
- Three activities per day
- Estimated costs that keep the total under ${user_specs['budget']}
- Simple, clear day-by-day breakdown

Format your response as plain text, using "Day 1:", "Day 2:", etc.
"""

# 5. Call the LLM
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ],
    temperature=0.7,
    max_tokens=600
)

itinerary_text = response.choices[0].message.content.strip()

# 6. Use or render the result
print("Generated Itinerary:\n")
print(itinerary_text)
