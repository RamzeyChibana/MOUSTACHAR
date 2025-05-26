import ollama
import json
import numpy as np
import faiss









def apply_keyword_boost(results,documents, keywords, top_k=5):
    """Boost documents containing keywords"""
    boosted = []
    for idx, score in results:
        
        content = documents[idx].lower()
        
        # Calculate keyword matches
        matches = sum(
            1 for kw in keywords
            if kw.lower() in content.lower() 
        )
        print(matches)
        boosted.append((idx, score * (1 + matches * 0.2)))  # 20% boost per match
    
    return sorted(boosted, key=lambda x: x[1], reverse=False)[:top_k]

def parse_query(query):
    """Extract filters and keywords from query using LLM"""
    response = ollama.generate(
        model="gemma3:4b",
        prompt=f"""Analyze this legal query and output:
        
        
        
        2. Important keywords with important sentances
     
        
        Query: {query}
        
        Output as JSON: {{
            "keywords": ["...", "..."]
        }}"""
    )
    
    # Clean the response
    raw_output = response["response"].strip()
    if '```json' in raw_output:
        raw_output = raw_output.split('```json')[1].split('```')[0]
    
    result = json.loads(raw_output)
    return result




def search_with_metadata(query_vector,embeddings, k=10):
    """Search with metadata filtering using Faiss"""
  
    
    # Create subset index
  
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Search subset
    distances, indices = index.search(query_vector, k)
    
    
    return [(i, dist) for i, dist in zip(indices[0], distances[0])] 