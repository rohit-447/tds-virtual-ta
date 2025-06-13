from flask import Flask, request, jsonify
import numpy as np
import faiss
import json
import base64
import io
import requests
from PIL import Image
import easyocr
from sentence_transformers import SentenceTransformer
import os

with open("all_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)
embeddings = np.load("embeddings.npy").astype("float32")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
index = faiss.read_index("faiss.index")
easyocr_reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image_b64):
    try:
        image = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
        result = easyocr_reader.readtext(np.array(image), detail=0)
        return " ".join(result).strip()
    except Exception as e:
        print("OCR ERROR:", e)
        return ""

def retrieve_chunks(query, top_k=50):
    query_emb = embedder.encode([query]).astype("float32")
    _, indices = index.search(query_emb, top_k)
    return [chunks[i] for i in indices[0]]

def get_links(retrieved_chunks):
    seen = set()
    links = []
    for c in retrieved_chunks:
        url = c.get("url", "")
        text = c.get("section_title") or c.get("topic_title") or c.get("filename") or "Reference"
        if url and url not in seen:
            links.append({"url": url, "text": text})
            seen.add(url)
        if len(links) >= 5:
            break
    return links

def generate_llm_answer(question, context):
    system_prompt = (
        "You are an expert TDS course assistant. Answer the question using only the provided context. "
        "Cite URLs from the context if relevant. If the answer is not in the context, say 'I don't know.'"
    )
    payload = {
        "model": "mistral",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question + '\n\nContext:\n' + context}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            json=payload,
            timeout=120
        )
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OLLAMA ERROR:", e)
        return "I couldn't generate an answer. Please try again."

app = Flask(__name__)

@app.route("/api/", methods=["POST"])
def answer():
    data = request.json
    question = data.get("question", "").strip()
    image_b64 = data.get("image", None)
    if not question:
        return jsonify({"error": "Question required"}), 400

    try:
        if image_b64:
            extracted_text = extract_text_from_image(image_b64)
            if extracted_text:
                question += " " + extracted_text

        retrieved = retrieve_chunks(question)
        context = "\n".join([c["text"] for c in retrieved[:10]])
        answer = generate_llm_answer(question, context)
        links = get_links(retrieved)
        return jsonify({"answer": answer, "links": links})
    except Exception as e:
        print("API ERROR:", e)
        return jsonify({"error": "Failed to process request", "details": str(e)}), 500

if __name__ == "__main__":
    app.run()
