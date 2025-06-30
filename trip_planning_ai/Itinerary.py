import os, json
from getpass import getpass
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# ——— 1. Authenticate
if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass("Enter your HF token: ")

# ——— 2. Prompt Template for Itinerary
activity_prompt = PromptTemplate.from_template("""
Create a {days}-day itinerary in {destination} for a "{travel_style}" trip.
Return it in this JSON format:
{{
  "itinerary": [
    {{
      "day": 1,
      "location": "Area Name",
      "activities": [
        {{
          "time": "8:00 AM",
          "description": "Start your day with a relaxing breakfast"
        }}
      ]
    }}
  ]
}}
Only return JSON.
""")

# ——— 3. Load Model
ep = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2", task="text-generation", max_new_tokens=1024)
llm = ChatHuggingFace(llm=ep)

# ——— 4. Chain + Input + Invoke
chain = activity_prompt | llm
variables = {
    "destination": "Toronto",
    "days": 3,
    "travel_style": "family"
}
resp = chain.invoke(variables)
raw = resp.content.strip()

# ——— 5. Parse JSON
try:
    j = json.loads(raw)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON:\n{raw}") from e

print("Itinerary JSON:", json.dumps(j, indent=2))