# nlp_vector_search_trip.py
"""
Example of NLP + Vector Search integration for trip planner
"""
import json
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = Flask(__name__)

# ----------- Data Preparation (One-Time) -----------
# Example data: list of POIs or hotels with textual descriptions
items = [
    {"id": 1, "name": "Budget Inn",   "description": "Affordable hotel two blocks from downtown, free breakfast", "price": 60},
    {"id": 2, "name": "Comfort Suites","description": "Mid-range hotel with gym and pool, close to the event venue",      "price": 120},
    {"id": 3, "name": "Luxury Stay",  "description": "High-end boutique hotel with spa and rooftop bar",                  "price": 200},
]

# Instantiate embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def build_index(items):
    # Compute embeddings for each item's description
    texts = [item["description"] for item in items]
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index and metadata
    faiss.write_index(index, "items.index")
    with open("items.json", "w") as f:
        json.dump(items, f)

# Build index at startup (or run once separately)
build_index(items)

# ----------- Load Index & Metadata -----------
index = faiss.read_index("items.index")
with open("items.json", "r") as f:
    items = json.load(f)

# ----------- Search Function -----------
def search_items(query: str, top_k: int = 3, max_price: float = None):
    # Embed query text
    q_emb = model.encode([query], convert_to_numpy=True)

    # Retrieve top-k similar
    distances, indices = index.search(q_emb, top_k)
    results = []

    for dist, idx in zip(distances[0], indices[0]):
        item = items[idx]
        # Filter by price if specified
        if max_price is None or item["price"] <= max_price:
            results.append({
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "price": item["price"],
                "score": float(dist)
            })
    return results

# ----------- Flask Endpoint Example -----------
@app.route("/search", methods=["POST"])
def search_endpoint():
    data = request.json
    query = data.get("query", "")
    max_price = data.get("max_price")
    top_k = data.get("top_k", 3)

    results = search_items(query, top_k=top_k, max_price=max_price)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True, port=5001)

# ----------- Usage Example -----------
# Send POST to http://localhost:5001/search with JSON body:
# {
#   "query": "cozy hotel near event", 
#   "max_price": 100,
#   "top_k": 2
# }
# Receives a list of semantically matched hotels under the price cap.
