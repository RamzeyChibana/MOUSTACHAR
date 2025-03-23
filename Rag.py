# First, install required packages
# pip install ollama chromadb instructor

import ollama
from chromadb import Documents, EmbeddingFunction, Client
from typing import List
import json
import re

def extract_fields(content,fields):
    """Extract legal keywords from content"""
    response = ollama.generate(
        model="deepseek-r1:32b",
        prompt=f"Extract filed for :\n{content}\n from those fields:{fields} fields: output as JSON"
    )
    raw_text = response["response"].strip()
    raw_output = response["response"].strip()
    if '```json' in raw_output:
        raw_output = raw_output.split('```json')[1].split('```')[0]
   
        
    print(raw_output)
    result = json.loads(raw_output)
    return result["field"]

with open("new_laws/chapters.txt", "r") as file:
    chapters = file.read()

with open("new_laws/fields.txt", "r") as file:
    fields = file.read()

query = "le prix du timbre du passeport"
print(extract_fields("Les règles posées par les articles 4 à 46 qui suivent sont d’application générale. Toutefois, desdispositions spéciales à chacun des produits peuvent les compléter ou y déroger.2",fields))