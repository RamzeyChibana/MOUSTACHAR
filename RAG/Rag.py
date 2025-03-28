import ollama
import json
import numpy as np
import faiss
from utils import filter_by_metadata,parse_query,search_with_metadata,apply_keyword_boost
import tqdm
import torch





# 1. Load Documents (Already Split)


class RagEngine():
    def __init__(self,laws_path="new_laws\\All_laws.json",fields_path="new_laws/fields.txt"):
        with open(f"{laws_path}", "r", encoding="utf-8") as file:
            laws = json.load(file)
        with open(f"{fields_path}", "r",encoding="utf-8") as file:
            self.fields = file.read()
        self.documents = []
        self.metadata = []
        pbar = tqdm.tqdm(total=len(laws))
        pbar.set_description("read All documents")
        for idx, law in enumerate(laws):
            law_title = list(law.keys())[0]
            content = str(law[law_title])
            
            # Store document and metadata
            self.documents.append(content)
            self.metadata.append({"idx":idx,"chapter":laws["metadata"]["chapter"],"field":laws["metadata"]["field"]})
            
            pbar.update(1)
        pbar.close()
        # 2. Compute Embeddings for Each Document Using Ollama

        pbar = tqdm.tqdm(total=len(laws))
        pbar.set_description("Compute embeddings of documents")
        all_embeddings = []
        for doc in self.documents:
            response = ollama.embeddings(
                model="snowflake-arctic-embed2",
                prompt=doc
            )
            all_embeddings.append(response["embedding"])
            pbar.update(1)
        pbar.close()
        embeddings_np = np.array(all_embeddings, dtype=np.float32)
        index = faiss.IndexFlatL2(embeddings_np.shape[1])
        index.add(embeddings_np)
        print(f"Faiss index size: {index.ntotal}")

    
    


    def run(self,query: str):
        # Extract filters and keywords
        result = parse_query(query)
        query_keywords = result["keywords"]
        query_filters = result["filters"]
        
        # Step 1: Filter by metadata
        eligible_indices = filter_by_metadata(query_filters,self.metadata)
        
        # Step 2: Vector search with metadata filtering
        query_embedding = ollama.embeddings(
            model="snowflake-arctic-embed2",
            prompt=query
        )["embedding"]
        
        # Search with metadata filtering
        vector_results = search_with_metadata(
            np.array([query_embedding], dtype=np.float32),
            eligible_indices,
            k=10
        )
        
        # Step 3: Keyword boosting
        boosted_results = apply_keyword_boost(vector_results, query_keywords)
        
        # Get top 3 results
        top_indices = [idx for idx, _ in boosted_results[:3]]
        context_docs = [self.documents[i] for i in top_indices]
        context_meta = [{k: self.metadata[k][i] for k in self.metadata} for i in top_indices]
        
        # Generate answer
        response = ollama.generate(
            model="mistral:latest",
            prompt=f"""Legal Context:
            {format_context(context_docs, context_meta)}
            
            Question: {query}
            Answer with legal citations:"""
        )
        return response["response"]



def format_context(docs, metas):
    """Format context with metadata"""
    return "\n\n".join(
        f"Law: {meta['title']}\nType: {meta['law_type']}\nContent: {doc}"
        for doc, meta in zip(docs, metas)
    )



# query = "c'est combien le prix de passeport  "
# print("Question:", query)
# answer = rag_query(query)
# print("-"*38,"answer","-"*38)
# print("Answer:", answer)
