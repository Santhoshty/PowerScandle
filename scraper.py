import requests
from bs4 import BeautifulSoup
import re


#Constants
#url = "https://vsbattles.fandom.com/wiki/Captain_America_(Marvel_Comics)"
#url= "https://vsbattles.fandom.com/wiki/Marvel_Comics"                             #edge case not a character
#url = "https://vsbattles.fandom.com/wiki/Collector"                                #edge case disambiguous page
#url = "https://vsbattles.fandom.com/wiki/Nightmare_Nurse_(DC_Comics)"              #edge case tier unknown
#url = "https://vsbattles.fandom.com/wiki/Happy_(Fairy_Tail)"                         #edge case Key? unsure
url = "https://vsbattles.fandom.com/wiki/Special:Random"


# Http Request
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    html_content = response.text # Giant String for all the html content

except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
    exit()


soup = BeautifulSoup(response.content, 'html.parser')


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
