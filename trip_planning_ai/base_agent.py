
from abc import ABC, abstractmethod
from typing import Any, Dict
import openai
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.warning("OPENAI_API_KEY not found in environment variables.")
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        pass
    
    def _make_llm_call(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to the LLM"""
        if not self.client:
            logging.error("OpenAI client is not initialized.")
            return "Error: OpenAI client is not initialized."
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"LLM call failed: {e}")
            return f"Error: {str(e)}"
        
        
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

# ——— 2. Create a template with variable and JSON instruction
template = """
Extract the following field from user input:
User says: "{user_input}"

Return output as strict JSON with keys: "length", "words".
Example: {{ "length": 5, "words": 1 }}
ONLY return the JSON output and nothing else.
"""
prompt = PromptTemplate.from_template(template)

# ——— 3. Load local or hosted model
# Local pipeline
# pipe = pipeline("text-generation", model="gpt2", tokenizer="gpt2", max_new_tokens=50, return_full_text=False)
# llm = HuggingFacePipeline(pipeline=pipe)

# Or hosted endpoint mode
from langchain_huggingface import HuggingFaceEndpoint
ep = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2", task="text-generation", max_new_tokens=50)
llm = ChatHuggingFace(llm=ep)

# ——— 4. Build and run chain
from langchain_core.runnables import Runnable

chain = prompt | llm

user_var = "Hello world!"
resp = chain.invoke({"user_input": user_var})
raw = resp.content.strip()

# ——— 5. Parse JSON safely
try:
    j = json.loads(raw)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON:\n{raw}") from e

print("Parsed JSON output:", j)
