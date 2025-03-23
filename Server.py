from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import json

import ollama
import json
import numpy as np
import faiss

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# 1. Load Documents (Already Split)
with open("laws_json\\All_laws.json", "r", encoding="utf-8") as file:
    laws = json.load(file)

# Extract full documents instead of chunking
documents = [str(l[list(l.keys())[0]]) for l in laws]
print(documents[:5])

# 2. Compute Embeddings for Each Document Using Ollama
all_embeddings = []
for doc in documents:
    response = ollama.embeddings(
        model="snowflake-arctic-embed2",
        prompt=doc
    )
    embedding = response["embedding"]
    if not embedding:
        print("Empty embedding for document:", doc[:100])
        continue
    all_embeddings.append(embedding)

# Convert embeddings to a NumPy array
embeddings_np = np.array(all_embeddings, dtype=np.float32)

# Determine embedding dimension
embedding_dim = embeddings_np.shape[1]
print(f"Embedding dimension: {embedding_dim}")

# 3. Build a Faiss Index
index = faiss.IndexFlatL2(embedding_dim)
index.add(embeddings_np)
print(f"Faiss index size: {index.ntotal}")

# 4. Query Function Using Faiss
def rag_query(query: str, temperature: float = 0.7):
    # Compute embedding for the query
    query_embedding = ollama.embeddings(
        model="snowflake-arctic-embed2",
        prompt=query
    )["embedding"]
    query_vector = np.array([query_embedding], dtype=np.float32)
    
    # Search the Faiss index for the 3 nearest documents
    k = 3
    distances, indices = index.search(query_vector, k)
    
    # Retrieve corresponding documents
    context_docs = [documents[i] for i in indices[0]]
    context = "\n\n".join(context_docs)
    print("---------------Context---------------")
    print(context)
    
    # Generate answer using Ollama with retrieved context
    response = ollama.generate(
        model="mistral:latest",
        
        prompt=f"""context:
        {context}
        olQuestion: {query}
        1- rephrase the question correctly
        2- answer from the context knowing that the information may be in one of them
        3-summarize the answer 

Answer:"""
    )
    
    return response["response"]
@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    if 'prompt' not in data:
        return jsonify({'error': 'No text provided'}), 400

    input_text = data['prompt']
    processed_text = input_text.upper() # Example processing (convert to uppercase)
      # Print the received data for debugging
    answer = rag_query(input_text)
        
    print("Question:", input_text)
    print("Answer:",answer)
    return jsonify({'reply': answer})

if __name__ == '__main__':
    app.run(debug=True)
