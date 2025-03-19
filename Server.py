from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    if 'prompt' not in data:
        return jsonify({'error': 'No text provided'}), 400

    input_text = data['prompt']
    processed_text = input_text.upper()+ "w skikm"  # Example processing (convert to uppercase)
    print(data)  # Print the received data for debugging
    return jsonify({'reply': processed_text})

if __name__ == '__main__':
    app.run(debug=True)
