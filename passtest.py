from flask import Flask, jsonify
from flask_cors import CORS
import random # Import the random module

app = Flask(__name__)
# Enable CORS for development
CORS(app) 

# Your data structure. I've updated the keys to match the database structure 
# from your scraper ('power_level' and 'image_url') for better integration.
python_scran_data = [
    { 
        "id": 1,
        "name": 'Darth Vader',
        "image_url": 'https://vignette.wikia.nocookie.net/vsbattles/images/2/29/Sandwormsschoenherr.jpg',
        "power_level": 75
    },
    {
        "id": 2,
        "name": 'Goku',
        "image_url": 'https://vignette.wikia.nocookie.net/vsbattles/images/b/be/Honey_Lemon_Render.png/revision/latest/scale-to-width-down/400?cb=20190404133937',
        "power_level": 90
    },
    {
        "id": 3,
        "name": 'Captain America',
        "image_url": 'https://vignette.wikia.nocookie.net/vsbattles/images/1/10/Captain_America_AOU_2.png',
        "power_level": 15
    },
    {
        "id": 4,
        "name": 'Cleopatra',
        "image_url": 'https://vignette.wikia.nocookie.net/vsbattles/images/b/b3/Cleopatra.png',
        "power_level": 40
    },
]

@app.route('/api/characters', methods=['GET'])
def get_all_characters():
    """Endpoint to return the full list of character data as JSON (for reference)."""
    return jsonify(python_scran_data)

@app.route('/api/characters/random', methods=['GET'])
def get_random_pair():
    """
    Endpoint to select two unique random characters and return them.
    This is the primary endpoint your JavaScript game will use.
    """
    # 1. Check for minimum data size
    if len(python_scran_data) < 2:
        return jsonify({"error": "Insufficient data to select a pair"}), 500
        
    # 2. Use random.sample to select two unique elements (no repeats)
    random_pair = random.sample(python_scran_data, 2)
    
    # 3. Return the pair as a JSON array
    return jsonify(random_pair)


if __name__ == '__main__':
    print("Starting Flask server...")
    print("Access: http://127.0.0.1:5000/api/characters/random to test the endpoint.")
    app.run(debug=True, port=5000)