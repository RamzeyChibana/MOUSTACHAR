import ollama
import json
import numpy as np
import faiss
import sys 
import os

from utils_im import parse_query,search_with_metadata,apply_keyword_boost
import tqdm
import matplotlib.pyplot as plt
import os






def show_one_by_one(image_paths):
    """
    Display each image in its own window. 
    Close the window to advance to the next image.
    """
    for img_path in image_paths:
        img = plt.imread(img_path)
        
        fig, ax = plt.subplots()
        ax.imshow(img)
        ax.set_title(img_path.split("/")[-1], fontsize=12)
        ax.axis("off")
        
        # This will block until you close the window:
        plt.show()
        
        # Close the figure explicitly to free memory before the next iteration
        plt.close(fig)

class RagEngine():
    def __init__(self,descriptions="descriptions.json"):
        with open(f"{descriptions}", "r", encoding="utf-8") as file:
            contexts = json.load(file)
        
        
        self.documents = []
        self.images = []
        self.metadata = []
        pbar = tqdm.tqdm(total=len(contexts))
        pbar.set_description("read All documents")
        for idx, context in enumerate(contexts):
            
            content = context["context"]
            
            if content != "" :
                self.documents.append(content)
                self.images.append(context["file"])
                
                self.metadata.append({"idx":idx,"file":context["file"]})
            
            pbar.update(1)
        pbar.close()
        
        data_path = "image_embeddings"
        files = os.listdir(data_path)
        if not files :
            pbar = tqdm.tqdm(total=len(contexts))
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
        result = parse_query(query)
        query_keywords = result["keywords"]
      
        print(f"keywordss : {result['keywords']}")
        
 
        
        # Step 2: Vector search with metadata filtering
        query_embedding = ollama.embeddings(
            model="nomic-embed-text:latest",
            prompt=query
        )["embedding"]

        
        vector_results = search_with_metadata(
            np.array([query_embedding], dtype=np.float32),
            self.embeddings_np,
            k=20
        )
        
        # Step 3: Keyword boosting
        boosted_results = apply_keyword_boost(vector_results,self.documents, query_keywords)
        print(boosted_results)
        # Get top 3 results
        top_indices = [idx for idx, _ in boosted_results]
        context_indices = [i for i,dist in boosted_results if dist<500]
        context_texts = [self.documents[i] for i in context_indices if self.metadata[i]["file"]==""]
        print(context_texts)
   
        context_images = [self.images[i] for i in context_indices if self.metadata[i]["file"]!=""]
        print(context_images)
        # show_one_by_one(context_images)

        # # Generate answer
        # response = ollama.generate(
        #     model="gemma3:4b",
        #     prompt=f"""Legal Context:
        #     {context_docs}
            
        #     Question: {query}
        #     act as legal advisor and answer based on context"""
        # )
        return context_images



def format_context(docs, metas):
    """Format context with metadata"""
    return "\n\n".join(
        f"Law: {meta['title']}\nType: {meta['law_type']}\nContent: {doc}"
        for doc, meta in zip(docs, metas)
    )

if __name__ == "__main__":
    rag = RagEngine()
    query_1 = "i want to know about Algeria the country"


    print("Question:", query_1)
    answer = rag.run(query_1)
    print("-"*38,"answer","-"*38)
    print("Answer:", answer)
