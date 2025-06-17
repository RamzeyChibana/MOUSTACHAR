from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
import os
import json
import sys
import ollama
import numpy as np
import faiss
from rag_images import RagEngine


app = Flask(__name__)
# run_with_ngrok(app)

CORS(app)

IMAGE_FOLDER = 'images'
ALWAYS_INCLUDE = 'dog.png'

#  ➤ Static route: serve any single image
@app.route('/images/<filename>')
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename)



@app.route('/process_text', methods=['POST'])
def get_images():
    data = request.get_json()
    query = data.get('name')
    if not query:
        return jsonify(error='No image name provided'), 400
    print(query)
    rag = RagEngine()
    answer = rag.run(query) 
    print(answer)
    to_send = answer
    # Validate
    for fn in to_send:
        path = os.path.join(IMAGE_FOLDER, fn)
        if not os.path.isfile(path):
            return jsonify(error=f'File not found: {fn}'), 404

    # Build URLs
    base = request.host_url.rstrip('/')
    urls = [f"{base}/images/{fn}" for fn in to_send]
    return jsonify(images=urls)

if __name__ == '__main__':
    app.run()
