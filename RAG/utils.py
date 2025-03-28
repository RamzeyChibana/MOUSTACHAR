import ollama
import json
import numpy as np
import faiss






def filter_by_metadata(query_metadata, metadata_list):
    """
    Returns indices of documents whose metadata matches the query.
    It checks if the query contains words from 'chapter' or 'file' metadata.
    """
    
    candidate_indices = []
    for i, meta in enumerate(metadata_list):
        chapter = meta["chapter"].lower()
        field = meta["field"].lower()
        # If the query includes either the chapter or file keywords, add the document index.
        if chapter in query_metadata["chapter"].lower or field in query_metadata["field"]:
            candidate_indices.append(i)
    return candidate_indices

def apply_keyword_boost(results, keywords, top_k=5):
    """Boost documents containing keywords"""
    boosted = []
    for idx, score in results:
        doc_keywords = metadata[idx]['keywords']
        content = documents[idx].lower()
        
        # Calculate keyword matches
        matches = sum(
            1 for kw in keywords
            if kw.lower() in content 
        )
        boosted.append((idx, score * (1 + matches * 0.2)))  # 20% boost per match
    
    return sorted(boosted, key=lambda x: x[1], reverse=True)[:top_k]

def parse_query(query,fields):
    """Extract filters and keywords from query using LLM"""
    response = ollama.generate(
        model="deepseek-r1:32b",
        prompt=f"""Analyze this legal query and output:
        1. Metadata filters (field , chapter name (Derived from the field and keywords)) 
        
        get field from those fields {fields}
        2. Important keywords
        3. ouput is french
        
        Query: {query}
        
        Output as JSON: {{
            "filters": {{"chapter": "...", "field": "..."}},
            "keywords": ["...", "..."]
        }}"""
    )
    
    # Clean the response
    raw_output = response["response"].strip()
    if '```json' in raw_output:
        raw_output = raw_output.split('```json')[1].split('```')[0]
    
    result = json.loads(raw_output)
    return result




def search_with_metadata(query_vector,embeddings,eligible_indices, k=10):
    """Search with metadata filtering using Faiss"""
    if not eligible_indices:
        return []
    
    # Create subset index
    subset_embeddings = embeddings[eligible_indices]
    subset_index = faiss.IndexFlatL2(subset_embeddings.shape[1])
    subset_index.add(subset_embeddings)
    
    # Search subset
    distances, indices = subset_index.search(query_vector, k)
    
    
    return [(eligible_indices[i], -dist) for i, dist in zip(indices[0], distances[0])]