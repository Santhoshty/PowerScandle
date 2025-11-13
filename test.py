import requests
from bs4 import BeautifulSoup
import re
import json
import time
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
# Enable CORS for development
CORS(app)

# --- CONSTANTS ---
DB_FILE = 'vsbattles_data.db'
TABLE_NAME = 'characters'
RANDOM_URL = "https://vsbattles.fandom.com/wiki/Special:Random"

###### METHODS ########

# HTTP Request Method also prints the URL taken from random
def requestBegin(url):
    # Http Request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        html_content = response.text
        recieved_url = response.url
        # print(f"URL : {recieved_url}") # Commented out for cleaner server output

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        # Return None or raise an exception to handle failure
        return None, None

    return BeautifulSoup(response.content, 'html.parser'), recieved_url

# Get The Tier Value in the Form of a String by Passing the Beautiful Soup Object
def getTier(soup_object):
    # Look for 'a' tag with string 'Tier' inside an infobox table
    tier_link = soup_object.find('a', string=re.compile(r'\s*Tier\s*'))

    if tier_link:
        # Navigate up to the parent element (e.g., a <td> or <th>)
        tier_label_tag = tier_link.parent

        # Search for the value, typically in the next sibling element
        # This assumes the structure is like: <td><b><a href="...">Tier</a></b></td><td><b>Tier Value</b></td>
        tier_value_bold_tag = tier_label_tag.find_next_sibling('td')

        if tier_value_bold_tag:
            # Look for the <b> tag inside the sibling
            final_b_tag = tier_value_bold_tag.find('b')

            if final_b_tag:
                tier_value = final_b_tag.get_text(strip=True)
                return tier_value

        # Fallback if the standard structure isn't found
        # print("Error: Could not find the tier value in the expected structure.")
        return None
    # else:
    #     print("Error: Could not find the <a> tag with string 'Tier'.")
    return None

# Get the Source Image in the Form of a String by Passing the Beautiful Soup Object
def getImageLink(soup_object):
    # Target the main character image often found in the infobox
    # It's usually the first big image. Using a selector that targets images in the main infobox

    infobox_img = soup_object.select_one('.infobox img[src]')

    if infobox_img:
        image_url = infobox_img['src']
        # Replace 'static' with 'vignette' to get a better quality image
        image_link = image_url.replace('static', 'vignette')
        return image_link

    return 'https://placehold.co/100x100/DC2626/ffffff?text=Image+Error'

# Get the rating Value From the Tier String
def ratingValue(string):

    value_map = {
        '11-C'      : 1, '11-B'      : 2, '11-A'      : 3,
        '10-C'      : 4, '10-B'      : 5, '10-A'      : 6,
        '9-C'       : 7, '9-B'       : 8, '9-A'       : 9,
        '8-C'       : 10, 'High 8-C'  : 11, '8-B'       : 12, '8-A'       : 13,
        'Low 7-C'   : 14, '7-C'       : 15, 'High 7-C'  : 16, 'Low 7-B'   : 17,
        '7-B'       : 18, '7-A'       : 19, 'High 7-A'  : 20,
        '6-C'       : 21, 'High 6-C'  : 22, '6-B'       : 23, 'High 6-B'  : 24,
        '6-A'       : 25, 'High 6-A'  : 26,
        '5-C'       : 27, 'Low 5-B'   : 28, '5-B'       : 29, '5-A'       : 30,
        'High 5-A'  : 31, 'Low 4-C'   : 32, '4-C'       : 33, 'High 4-C'  : 34,
        '4-B'       : 35, '4-A'       : 36,
        '3-C'       : 37, '3-B'       : 38, '3-A'       : 39, 'High 3-A'  : 40,
        'Low 2-C'   : 41, '2-C'       : 42, '2-B'       : 43, '2-A'       : 44,
        'Low 1-C'   : 45, '1-C'       : 46, 'High 1-C'  : 47, '1-B'       : 48,
        'High 1-B'  : 49, 'Low 1-A'   : 50, '1-A'       : 51, 'High 1-A'  : 52,
        '0'         : 53,
        # Handling edge cases
        'Unknown'   : 54, # Set to a high value to avoid being the default answer
        'Varies'    : 12 # Mid-range value
    }

    # Return the mapped value or 0 for unmapped tiers
    return value_map.get(string, 0)

# --- CORE LOGIC FUNCTION ---
def scrape_character_data(num_characters=2):

    data = []
    count = 0
    reiterations = 0
    max_reiterations = 10

    while count < num_characters and reiterations < max_reiterations:

        soup, recieved_url = requestBegin(RANDOM_URL)

        if soup is None:
             reiterations += 1
             time.sleep(1)
             continue

        # 1. Character Name
        page_title = soup.title.string
        character_name = page_title.split(' |',1)[0]

        # 2. Tier Value
        tier_value = getTier(soup)

        # Skip if Tier is invalid (Tier is None, 'Varies', or 'Unknown')
        # We allow 'Varies' and 'Unknown' in ratingValue, but often these pages
        # are not ideal for simple comparison games. Let's strictly skip None.
        if tier_value is None:
            reiterations += 1
            # print(f"Tier Invalid (None) - {reiterations} reiteration. URL: {recieved_url}")
            time.sleep(0.5)
            continue

        # 3. Source Image
        image_link = getImageLink(soup)

        # 4. Power Level Rating
        power_level = ratingValue(tier_value)

        # 5. Check for valid power level (0 is often an unmapped tier)
        # If the power level is 0, skip this character.
        if power_level == 0 and tier_value not in ['Varies', 'Unknown']:
            reiterations += 1
            # print(f"Power Level Invalid (0) - {reiterations} reiteration. URL: {recieved_url}")
            time.sleep(0.5)
            continue

        # Data collection successful
        keys = ["Character", "Tier", "Source Image", "Power Level"]
        value = [character_name, tier_value, image_link, power_level]
        character_data = dict(zip(keys, value))

        # print(f"Collected: {character_name} ({tier_value}) from {recieved_url}")
        data.append(character_data)
        count += 1
        time.sleep(0.5) # Be respectful to the server

    if reiterations == max_reiterations and count < num_characters:
        print(f"Warning: Failed to collect {num_characters} characters after {max_reiterations} attempts.")

    return data


# --- FLASK ROUTE ---
@app.route("/api/data", methods = ['GET'])
@cross_origin()
def get_data():
    """
    Scrapes two random character entries every time this endpoint is requested.
    """
    try:
        data = scrape_character_data(num_characters=2)
        if len(data) == 2:
            return jsonify(data)
        else:
            # If we couldn't scrape 2 characters, return an error message
            return jsonify({"error": "Failed to retrieve two valid character entries."}), 503

    except Exception as e:
        print(f"An unexpected error occurred in get_data: {e}")
        return jsonify({"error": "Internal server error during scraping."}), 500


if __name__ == '__main__':
    # Running the app on the host and port specified in the JavaScript snippet
    print("Starting Flask server on http://127.0.0.1:8004/api/data...")
    # NOTE: The scraping logic is no longer run here, only when the route is hit.
    app.run(host = "127.0.0.1", port=8004)
