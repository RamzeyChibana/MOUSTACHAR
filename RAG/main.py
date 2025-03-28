# First, install required packages:
# pip install ollama faiss-cpu numpy

import ollama
import json
import numpy as np
import faiss

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
        model="nomic-embed-text",
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
        model="nomic-embed-text",
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
        prompt=f"""Answer the question using only this context:
{context}

Question: {query}
Answer:"""
    )
    
    return response["response"]

# 5. Test Query
if __name__ == "__main__":
    query = "c'est combien les taxes relatives aux bateaux"
    print("Question:", query)
    print("Answer:", rag_query(query))
