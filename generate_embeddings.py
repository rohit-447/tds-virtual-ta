import numpy as np
import json
from sentence_transformers import SentenceTransformer

def generate_embeddings():
    with open("all_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    texts = [c["text"] for c in chunks]
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(texts, show_progress_bar=True)
    np.save("embeddings.npy", embeddings)

if __name__ == "__main__":
    generate_embeddings()
