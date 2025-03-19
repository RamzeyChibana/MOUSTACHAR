# First, install required packages
# pip install ollama chromadb instructor

import ollama
from chromadb import Documents, EmbeddingFunction, Client
from typing import List
import instructor
from instructor import Instructor

# 1. Prepare Documents
documents = [
    "Ollama is a lightweight framework for running large language models locally",
    "ChromaDB is an open-source embedding database for building AI applications",
    "RAG stands for Retrieval-Augmented Generation used in AI systems",
    "LLMs can generate human-like text but need grounding with factual information",
]

# Save documents to a text file (for demonstration)
with open("data.txt", "w") as f:
    f.write("\n".join(documents))

# 2. Document Processing
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents():
    with open("data.txt") as f:
        text = f.read()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        length_function=len
    )
    return text_splitter.split_text(text)

chunks = chunk_documents()

# 3. Embedding Function using Ollama
class OllamaEmbeddingFunction(EmbeddingFunction):
    def __call__(self, texts: Documents) -> List[Embedding]:
        embeddings = []
        for text in texts:
            response = ollama.embeddings(
                model="nomic-embed-text",
                prompt=text
            )
            embeddings.append(response["embedding"])
        return embeddings


client = Client()
collection = client.create_collection(
    name="rag_demo",
    embedding_function=OllamaEmbeddingFunction()
)

# documents to collection
collection.add(
    ids=[str(i) for i in range(len(chunks))],
    documents=chunks
)


def rag_query(query: str, temperature: float = 0.7):
    #  embedding
    query_embedding = ollama.embeddings(
        model="nomic-embed-text",
        prompt=query
    )["embedding"]
    

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    

    context = "\n\n".join(results["documents"][0])
    
    
    response = ollama.generate(
        model="llama2",
        prompt=f"""Answer the question using only this context:
        {context}
        
        Question: {query}
        Answer:"""
    )
    
    return response["response"]


if __name__ == "__main__":
    query = "What is RAG used for?"
    print("Question:", query)
    print("Answer:", rag_query(query))