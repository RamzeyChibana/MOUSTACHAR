from flask import Flask, send_from_directory
from flask_ngrok import run_with_ngrok
import os

app = Flask(__name__)
run_with_ngrok(app)  # This wraps the app with Ngrok

# Folder where your images are stored
IMAGE_FOLDER = os.path.join(os.getcwd(), 'images')

# Serve the image by filename
@app.route('/image/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# Optional: Homepage
@app.route('/')
def index():
    return '<h1>Flask + Ngrok</h1><img src="/images/dog.png" width="300"/>'

if __name__ == '__main__':
    app.run()
