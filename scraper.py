import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import os
from flask import Flask, jsonify
from flask_cors import CORS # Required for development to allow cross-origin requests

app = Flask(__name__)
# Enable CORS for development
CORS(app)

#Constants
#url = "https://vsbattles.fandom.com/wiki/Captain_America_(Marvel_Comics)"
#url= "https://vsbattles.fandom.com/wiki/Marvel_Comics"                             #edge case not a character
#url = "https://vsbattles.fandom.com/wiki/Collector"                                #edge case disambiguous page
#url = "https://vsbattles.fandom.com/wiki/Nightmare_Nurse_(DC_Comics)"              #edge case tier unknown
#url = "https://vsbattles.fandom.com/wiki/Happy_(Fairy_Tail)"                       #edge case Key? unsure
url = "https://vsbattles.fandom.com/wiki/Special:Random"
#url = "https://vsbattles.fandom.com/wiki/Cleopatra_(Fate)"
#url = "https://vsbattles.fandom.com/wiki/The_Darkhold_(Marvel_Cinematic_Universe)" #edge case tier unknown

DB_FILE = 'vsbattles_data.db'
TABLE_NAME = 'characters'

#Methods

def ratingValue(string):
    
    value_map = {
        '11-C'      : 1,
        '11-B'      : 2,
        '11-A'      : 3,
        '10-C'      : 4,
        '10-B'      : 5,
        '10-A'      : 6,
        '9-C'       : 7,
        '9-B'       : 8,
        '9-A'       : 9,
        '8-C'       : 10,
        'High 8-C'  : 11,
        '8-B'       : 12,
        '8-A'       : 13,
        'Low 7-C'   : 14,
        '7-C'       : 15,
        'High 7-C'  : 16,
        'Low 7-B'   : 17,
        '7-B'       : 18,
        '7-A'       : 19,
        'High 7-A'  : 20,
        '6-C'       : 21,
        'High 6-C'  : 22,
        '6-B'       : 23,
        'High 6-B'  : 24,
        '6-A'       : 25,
        'High 6-A'  : 26,
        '5-C'       : 27,
        'Low 5-B'   : 28,
        '5-B'       : 29,
        '5-A'       : 30,
        'High 5-A'  : 31,
        'Low 4-C'   : 32,
        '4-C'       : 33,
        'High 4-C'  : 34,
        '4-B'       : 35,
        '4-A'       : 36,
        '3-C'       : 37,
        '3-B'       : 38,
        '3-A'       : 39,
        'High 3-A'  : 40,
        'Low 2-C'   : 41,
        '2-C'       : 42,
        '2-B'       : 43,
        '2-A'       : 44,
        'Low 1-C'   : 45,
        '1-C'       : 46,
        'High 1-C'  : 47,
        '1-B'       : 48,
        'High 1-B'  : 49,
        'Low 1-A'   : 50,
        '1-A'       : 51,
        'High 1-A'  : 52,
        '0'         : 53,
        'Unknown'   : 54             
    }

    return value_map.get(string, 0)


# Http Request
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    html_content = response.text # Giant String for all the html content

except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
    exit()

soup = BeautifulSoup(response.content, 'html.parser')

# Get URL
final_url = response.url
print(f"URL : {final_url}")

# Character Name
page_title = soup.title.string
character_name = page_title.split(' |',1)[0]
print(f"Character Name: {character_name}")


# Tier Ranking
tier_link = soup.find('a', string='Tier')

if tier_link:

    tier_label_bold_tag = tier_link.parent
    
    tier_value_bold_tag = tier_label_bold_tag.find_next_sibling('b')
    
    if tier_value_bold_tag:
        tier_value = tier_value_bold_tag.get_text(strip=True)
        print(f"Tier value: {tier_value}")

    else:

        print("Error: Could not find the next <b> tag containing the tier value.")
else:

    print("Error: Could not find the <a> tag with string 'Tier'.")


# Source Image

image_elements = soup.find_all('img')

image_urls = []

for img in image_elements:
    if 'src' in img.attrs:  # Check if the 'src' attribute exists
        image_urls.append(img['src'])

#for url in image_urls:
#    print(url)

image_link = image_urls[2].replace('static','vignette')

print(f"Source Image: {image_link}")

power_level = ratingValue(tier_value)

print(f"Power Level: {power_level}")


######## Connect to the database #########

conn = None

try:

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 3. Create the table if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            tier_string TEXT,
            power_level INTEGER,
            url TEXT,
            image_url TEXT
        )
    """)
    conn.commit()

    # 4. Prepare data for insertion (using a tuple)
    data_to_insert = (
        character_name,
        tier_value,
        power_level,
        final_url,
        image_link
    )

    # 5. Insert data. Use ON CONFLICT IGNORE to skip if the character name already exists
    # This prevents errors if you run the random scraper multiple times and hit the same page.
    insert_query = f"""
        INSERT INTO {TABLE_NAME} (name, tier_string, power_level, url, image_url)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO NOTHING;
    """
    cursor.execute(insert_query, data_to_insert)
    conn.commit()
    print(f"\n✅ Data for **{character_name}** successfully inserted/updated in '{DB_FILE}'.")

except sqlite3.Error as e:
    print(f"\n❌ Database error occurred: {e}")

finally:
    # 6. Close the connection
    if conn:
        conn.close()

# Example of how to read data back (optional)
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    count = cursor.fetchone()[0]
    print(f"Current total characters in database: {count}")
except sqlite3.Error as e:
    print(f"Error reading database count: {e}")
finally:
    if conn:
        conn.close()