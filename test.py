url = "https://vsbattles.fandom.com/wiki/Special:Random"

import requests
from bs4 import BeautifulSoup

# Http Request
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    html_content = response.text # Giant String for all the html content

except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
    exit()


soup = BeautifulSoup(response.content, 'html.parser')

image_elements = soup.find_all('img')

image_urls = []

for img in image_elements:
    if 'src' in img.attrs:  # Check if the 'src' attribute exists
        image_urls.append(img['src'])

for url in image_urls:
    print(url)

try:
    print(f"\nThe Source Image is: {image_urls[2]}")
except IndexError:
    # Catch the error if index 2 doesn't exist (i.e., list has < 3 elements)
    print("\nAn IndexError occurred.")
    print(f"The list 'image_urls' has no element at index 2. Total images found: {len(image_urls)}")