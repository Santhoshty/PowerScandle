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
        "name": 'Mitsuru Kirijo',
        "tier_string": 'Low 2-C',
        "power_level": '41',
        "url": 'https://vsbattles.fandom.com/wiki/Mitsuru_Kirijo',
        "image_url": 'https://vignette.wikia.nocookie.net/vsbattles/images/d/d4/Mitsuru_Kirijo_render.png/revision/latest?cb=20170506143614',
    },
    {
        "id": 2,
        "name": 'Goku',
        "image_url": 'https://vignette.wikia.nocookie.net/vsbattles/images/b/be/Honey_Lemon_Render.png/revision/latest/scale-to-width-down/400?cb=20190404133937',
        "power_level": 90
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