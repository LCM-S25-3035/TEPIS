# Install dependencies:
# pip install langchain-huggingface transformers torch

import os, json
from getpass import getpass
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import pipeline

# ——— 1. Authenticate
if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass("Enter your HF token: ")

# ——— 2. Create hotel recommendation prompt template
hotel_prompt_template = """
Generate a list of 5 famous hotels in {destination}. Format the response as JSON only:

{{
  "hotels": [
    {{
      "name": "Hotel Name",
      "description": "Brief description of the hotel",
      "rating": 4.5,
      "price_category": "Luxury"
    }}
  ]
}}
Return only the JSON. No explanations.
"""

prompt = PromptTemplate.from_template(hotel_prompt_template)

# ——— 3. Load hosted endpoint model
from langchain_huggingface import HuggingFaceEndpoint
ep = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2", task="text-generation", max_new_tokens=512)
llm = ChatHuggingFace(llm=ep)

# ——— 4. Build and run chain
from langchain_core.runnables import Runnable

chain = prompt | llm

destination = "Toronto"
resp = chain.invoke({"destination": destination})
raw = resp.content.strip()

# ——— 5. Parse JSON safely
try:
    j = json.loads(raw)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON:\n{raw}") from e

print("Parsed JSON output:", json.dumps(j, indent=2))
