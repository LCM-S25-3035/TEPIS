import os
import json
from getpass import getpass
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# -------------------- Authentication --------------------
def authenticate_hf_token():
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass("Enter your HF token: ")

# -------------------- Prompt Template --------------------
def get_hotel_prompt():
    return PromptTemplate.from_template("""
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
    """)

# -------------------- Model Loader --------------------
def load_llm():
    ep = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        task="text-generation",
        max_new_tokens=512
    )
    return ChatHuggingFace(llm=ep)

# -------------------- Hotel Recommendation --------------------
def get_hotel_recommendations(destination):
    prompt = get_hotel_prompt()
    llm = load_llm()
    chain = prompt | llm

    resp = chain.invoke({"destination": destination})
    raw = resp.content.strip() if hasattr(resp, 'content') else ""

    if not raw:
        raise ValueError("Model returned empty response.")

    try:
        hotels_json = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON:\n{raw}") from e

    return hotels_json

# -------------------- Main Execution --------------------
if __name__ == "__main__":
    authenticate_hf_token()
    destination = "Toronto"  # Example; replace as needed
    hotels = get_hotel_recommendations(destination)
    print("Parsed JSON output:", json.dumps(hotels, indent=2))