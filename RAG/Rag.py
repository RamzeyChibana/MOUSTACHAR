import ollama
import json
import numpy as np
import faiss
from utils import filter_by_metadata,parse_query,search_with_metadata,apply_keyword_boost
import tqdm

import os








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
            
            if content != "" :
                self.documents.append(content)
                self.metadata.append({"idx":idx,"chapter":law["metadata"]["chapter"],"field":law["metadata"]["file"]})
            
            pbar.update(1)
        pbar.close()
        # 2. Compute Embeddings for Each Document Using Ollama
        data_path = "embeddings/"
        files = os.listdir(data_path)
        if not files :
            pbar = tqdm.tqdm(total=len(laws))
            pbar.set_description("Compute embeddings of documents")
            all_embeddings = []
            for doc in self.documents:
                response = ollama.embeddings(
                    model="nomic-embed-text:latest",
                    prompt=doc
                )
                all_embeddings.append(response["embedding"])
                pbar.update(1)
            pbar.close()
            embeddings_np = np.array(all_embeddings, dtype=np.float32)
         
            print(np.save(f"{os.path.join(data_path,'embeddigns.npy')}",embeddings_np))
        else :
            embeddings_np = np.load(f"{os.path.join(data_path,'embeddigns.npy')}")
        
        self.embeddings_np = embeddings_np

        index = faiss.IndexFlatL2(embeddings_np.shape[1])
        index.add(embeddings_np)
        print(f"Faiss index size: {index.ntotal}")

    
    


    def run(self,query: str):
        # Extract filters and keywords
        result = parse_query(query,self.fields)
        query_keywords = result["keywords"]
        query_filters = result["filters"]
        print(f"filters : {result['filters']}")
        print(f"keywordss : {result['keywords']}")
        # Step 1: Filter by metadata
        eligible_indices = filter_by_metadata(query_filters,query_keywords,self.metadata,self.documents)
        
        # Step 2: Vector search with metadata filtering
        query_embedding = ollama.embeddings(
            model="nomic-embed-text:latest",
            prompt=query
        )["embedding"]
        print(len(eligible_indices))
        # Search with metadata filtering
        vector_results = search_with_metadata(
            np.array([query_embedding], dtype=np.float32),
            self.embeddings_np,
            eligible_indices,
            k=10
        )
        
        # Step 3: Keyword boosting
        boosted_results = apply_keyword_boost(vector_results,self.documents, query_keywords)
        
        # Get top 3 results
        top_indices = [idx for idx, _ in boosted_results[:3]]
        context_docs = [self.documents[i] for i in top_indices]
        # context_meta = [{k: self.metadata[k][i] for k in self.metadata} for i in top_indices]
        print(context_docs)
        # Generate answer
        response = ollama.generate(
            model="deepseek-r1:7b",
            prompt=f"""Legal Context:
            {context_docs}
            act as legal advisor and answer based on context
            Question: {query}
            Answer in French
            """
        )
        return response["response"]



def format_context(docs, metas):
    """Format context with metadata"""
    return "\n\n".join(
        f"Law: {meta['title']}\nType: {meta['law_type']}\nContent: {doc}"
        for doc, meta in zip(docs, metas)
    )



