import os
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from flask import Flask, jsonify
from flask_cors import CORS

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Constants
URL = "https://vsbattles.fandom.com/wiki/Special:Random"

###### METHODS ########

# HTTP Request Method also prints the url taken from random
def requestBegin(target_url):
    try:
        response = requests.get(target_url)
        response.raise_for_status()
        html_content = response.text
        recieved_url = response.url
        # print(f"URL : {recieved_url}") # Print statements are fine, but can be verbose in production logs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        # In an API context, consider raising an exception or returning an error response
        return None, None 

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup, recieved_url

# Get The Tier Value
def getTier(soup_object):
    tier_link = soup_object.find('a', string='Tier')
    if tier_link:
        tier_label_bold_tag = tier_link.parent
        tier_value_bold_tag = tier_label_bold_tag.find_next_sibling('b')
        if tier_value_bold_tag:
            return tier_value_bold_tag.get_text(strip=True)
    return None

# Get the Source Image
def getImageLink(soup_object):
    infobox = soup_object.find('aside')
    if infobox:
        main_image = infobox.find('img')
        if main_image:
            image_src = main_image.get('src', '')
            if 'static.wikia.nocookie' in image_src:
                return image_src.replace('static','vignette')
    
    # Fallback method (kept simplified)
    image_elements = soup_object.find_all('img')
    valid_image_count = 0
    for img in image_elements:
        image_src = img.get('src', '')
        if 'static.wikia.nocookie' in image_src:
            valid_image_count += 1
            if valid_image_count == 3:
                return image_src.replace('static','vignette')
    return None

# Get the rating Value From the Tier String
def ratingValue(string):
    value_map = {
        '11-C': 10, '11-B': 20, '11-A': 30, '10-C': 40, '10-B': 50, '10-A': 60,
        '9-C': 70, '9-B': 80, '9-A': 90, '8-C': 100, 'High 8-C': 110, '8-B': 120,
        '8-A': 130, 'Low 7-C': 140, '7-C': 150, 'High 7-C': 160, 'Low 7-B': 170,
        '7-B': 180, '7-A': 190, 'High 7-A': 200, '6-C': 210, 'High 6-C': 220,
        'Low 6-B': 225, '6-B': 230, 'High 6-B': 240, '6-A': 250, 'High 6-A': 260,
        '5-C': 270, 'Low 5-B': 280, '5-B': 290, '5-A': 300, 'High 5-A': 310,
        'Low 4-C': 320, '4-C': 330, 'High 4-C': 340, '4-B': 350, '4-A': 360,
        '3-C': 370, '3-B': 380, '3-A': 390, 'High 3-A': 400, 'Low 2-C': 410,
        '2-C': 420, '2-B': 430, '2-A': 440, 'Low 1-C': 450, '1-C': 460,
        'High 1-C': 470, '1-B': 480, 'High 1-B': 490, 'Low 1-A': 500, '1-A': 510,
        'High 1-A': 520, '0': 530, 'Unknown': 365, 'Varies': 120
    }
    return value_map.get(string, 0)

# --- API Endpoint (Runs the Scraping Logic) ---

@app.route("/api/data", methods = ['GET'])
def get_data():
    
    data = []
    keys = ["Character", "Tier", "Source Image", "Power Level", "URL"]
    count = 0
    reiterations = 0
    MAX_COUNT = 21 # Scrape 21 characters per request

    while count < MAX_COUNT:
        
        soup, character_url = requestBegin(URL)

        if not soup: # Handle requestBegin failure
            continue
            
        value = []

        # Character Name
        page_title = soup.title.string
        character_name = page_title.split(' |',1)[0]
        value.append(character_name)
        
        # Tier Value
        tier_value = getTier(soup)

        if tier_value is None:
            reiterations += 1
            if reiterations >= 10:
                break # Stop after 10 failed attempts
            time.sleep(0.2)
            continue # Try again
        
        value.append(tier_value)

        # Image Link
        image_link = getImageLink(soup)
        value.append(image_link)

        # Power Level
        power_level = ratingValue(tier_value)
        value.append(power_level)
        
        # URL
        value.append(character_url)

        # Combine keys and values into a single dictionary
        character_data = dict(zip(keys, value))
        data.append(character_data)

        count += 1
        time.sleep(0.2)

    if not data:
        # Return an error if no data was successfully collected
        return jsonify({"error": "Failed to scrape any data. Check source site or logic."}), 500

    return jsonify(data) #test code