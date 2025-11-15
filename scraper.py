import requests
from bs4 import BeautifulSoup
import re
import json
import time
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin # Required for development to allow cross-origin requests

app = Flask(__name__)
# Enable CORS for development
CORS(app)

#Constants
#url = "https://vsbattles.fandom.com/wiki/Captain_America_(Marvel_Comics)"
#url= "https://vsbattles.fandom.com/wiki/Marvel_Comics"                             #edge case not a character
#url = "https://vsbattles.fandom.com/wiki/Collector"                                #edge case disambiguous page
#url = "https://vsbattles.fandom.com/wiki/Nightmare_Nurse_(DC_Comics)"              #edge case tier unknown
#url = "https://vsbattles.fandom.com/wiki/Happy_(Fairy_Tail)"                       #edge case Key? unsure
url = "https://vsbattles.fandom.com/wiki/Izuku_Midoriya_(Deku)_(Pre-Final_Act)"
#url = "https://vsbattles.fandom.com/wiki/The_Darkhold_(Marvel_Cinematic_Universe)" #edge case tier unknown


###### METHODS ########

# HTTP Request Method also prints the url taken from random

def requestBegin(target_url):
# Http Request
    try:
        response = requests.get(target_url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        html_content = response.text # Giant String for all the html content
        recieved_url = response.url
        print(f"URL : {recieved_url}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        exit()

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup, recieved_url

# Get The Tier Value in the Form of a String by Passing the Beautiful Soup Object
# If String is 'none' restart

def getTier(soup_object):

    tier_link = soup_object.find('a', string='Tier')

    if tier_link:

        tier_label_bold_tag = tier_link.parent
        
        tier_value_bold_tag = tier_label_bold_tag.find_next_sibling('b')
        
        if tier_value_bold_tag:
            tier_value = tier_value_bold_tag.get_text(strip=True)
            return tier_value

        else:

            print("Error: Could not find the next <b> tag containing the tier value.")
    else:

        print("Error: Could not find the <a> tag with string 'Tier'.")

# Get the Source Image in the Form of a String by Passing the Beautiful Soup Object

def getImageLink(soup_object):


    """
    Finds the primary character image located within the main character infobox,
    or falls back to the counter method if the infobox selector fails.
    """
    
    # Attempt 1: Target the image within the main information box (<aside> tag)
    infobox = soup_object.find('aside')
    
    if infobox:
        # Find the first <img> tag within that infobox
        main_image = infobox.find('img')
        
        if main_image:
            image_src = main_image.get('src', '')
            
            if 'static.wikia.nocookie' in image_src:
                print("Found image via infobox method.")
                return image_src.replace('static','vignette')
        
        # If we find the aside but the image inside is not what we expect,
        # we might need to broaden our search within the aside, but for now,
        # we proceed to the fallback method.
        print("Image within infobox did not match expected pattern or structure.")

    # Attempt 2 (Fallback): Use the counter method across the entire page
    print("Falling back to the full page scan (counter method).")
    image_elements = soup_object.find_all('img')
    valid_image_count = 0
    
    for img in image_elements:
        image_src = img.get('src', '')
        
        if 'static.wikia.nocookie' in image_src:
            valid_image_count += 1
            
            # If this is the third valid image found
            if valid_image_count == 3:
                print("Found image via fallback counter method.")
                return image_src.replace('static','vignette')
            
    # If all methods fail
    print(f"Error: Only {valid_image_count} suitable images found. Could not reliably find the main image.")
    return None

# Get the rating Value From the Tier String

def ratingValue(string):
    
    value_map = {
        '11-C'      : 10,
        '11-B'      : 20,
        '11-A'      : 30,
        '10-C'      : 40,
        '10-B'      : 50,
        '10-A'      : 60,
        '9-C'       : 70,
        '9-B'       : 80,
        '9-A'       : 90,
        '8-C'       : 100,
        'High 8-C'  : 110,
        '8-B'       : 120,
        '8-A'       : 130,
        'Low 7-C'   : 140,
        '7-C'       : 150,
        'High 7-C'  : 160,
        'Low 7-B'   : 170,
        '7-B'       : 180,
        '7-A'       : 190,
        'High 7-A'  : 200,
        '6-C'       : 210,
        'High 6-C'  : 220,
        'Low 6-B'   : 225,
        '6-B'       : 230,
        'High 6-B'  : 240,
        '6-A'       : 250,
        'High 6-A'  : 260,
        '5-C'       : 270,
        'Low 5-B'   : 280,
        '5-B'       : 290,
        '5-A'       : 300,
        'High 5-A'  : 310,
        'Low 4-C'   : 320,
        '4-C'       : 330,
        'High 4-C'  : 340,
        '4-B'       : 350,
        '4-A'       : 360,
        '3-C'       : 370,
        '3-B'       : 380,
        '3-A'       : 390,
        'High 3-A'  : 400,
        'Low 2-C'   : 410,
        '2-C'       : 420,
        '2-B'       : 430,
        '2-A'       : 440,
        'Low 1-C'   : 450,
        '1-C'       : 460,
        'High 1-C'  : 470,
        '1-B'       : 480,
        'High 1-B'  : 490,
        'Low 1-A'   : 500,
        '1-A'       : 510,
        'High 1-A'  : 520,
        '0'         : 530,
        'Unknown'   : 540, #Darkhold
        'Varies'    : 120 # Thaal Sinestro            
    }

    return value_map.get(string, 0)

count = 0
reiterations = 0

#Dictionary
data = []
keys = ["Character", "Tier", "Source Image", "Power Level", "URL"]

while count < 21:

    soup, character_url = requestBegin(url)
    value = []

    # Character Name
    page_title = soup.title.string
    character_name = page_title.split(' |',1)[0]
    print(f"Character Name: {character_name}")
    value.append(character_name)
    
    #Tier Value
    tier_value = getTier(soup)

    if tier_value is None:
        reiterations += 1
        if reiterations == 10:
            exit()

        print (f"Tier Invalid - {reiterations} reiteration")
        time.sleep(0.2)
        continue

    print(f"Tier: {tier_value}")
    value.append(tier_value)

    image_link = getImageLink(soup)
    print(f"Source Image: {image_link}")
    value.append(image_link)

    power_level = ratingValue(tier_value)
    print(f"Power Level: {power_level}")
    value.append(power_level)
    
    print(f"URL: {character_url}\n")
    value.append(character_url)

    # Combine keys and values into a single dictionary using zip()
    character_data = dict(zip(keys, value))
    data.append(character_data) # Add the dictionary to the 

    count += 1
    time.sleep(0.2)

json_data = json.dumps(data, indent=4)
print("Collected Data:")
print(json_data)

app = Flask(__name__)

@app.route("/api/data", methods = ['GET'])
@cross_origin() 
def get_data():
    return jsonify(data)

if __name__ == '__main__':
    # Running the app on the host and port specified in the JavaScript snippet
    print("Starting Flask server on http://127.0.0.1:8004/api/data...")
    app.run(host = "127.0.0.1", port=8004)