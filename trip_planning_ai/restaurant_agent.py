import os, json
from getpass import getpass
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# ——— 1. Authenticate
if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass("Enter your HF token: ")

# ——— 2. Prompt Template for Restaurants
restaurant_prompt = PromptTemplate.from_template("""
List 5 top restaurants in {destination} in JSON:
{{
  "restaurants": [
    {{
      "name": "Restaurant Name",
      "cuisine": "Cuisine",
      "description": "Short description",
      "rating": 4.7,
      "price_range": "$$"
    }}
  ]
}}
Only output JSON.
""")

# ——— 3. Load Model
ep = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2", task="text-generation", max_new_tokens=512)
llm = ChatHuggingFace(llm=ep)

# ——— 4. Chain + Invoke
chain = restaurant_prompt | llm
destination = "Toronto"
resp = chain.invoke({"destination": destination})
raw = resp.content.strip()

# ——— 5. Parse JSON safely
try:
    j = json.loads(raw)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON:\n{raw}") from e

print("Top Restaurants JSON:", json.dumps(j, indent=2))