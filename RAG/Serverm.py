from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import json
from Rag import RagEngine
import ollama
import json
import numpy as np
import faiss
import re

def remove_think_section(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    if 'prompt' not in data:
        return jsonify({'error': 'No text provided'}), 400

    query = data['prompt']
    rag = RagEngine()
    answer = rag.run(query) 
      # Print the received data for debugging
    
        
    print("Question:", query)
    print("Answer:",answer)
    return jsonify({'reply': remove_think_section(answer)})

if __name__ == '__main__':
    app.run(debug=True)
