from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import random

def DrawArtWindow(draw, startingYPos):
    # Loading fonts
    try:
        small_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=15)
        medium_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=28)
        large_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=36)
    except IOError:
        small_lato_font_regular = ImageFont.load_default()
        medium_lato_font_regular = ImageFont.load_default()
        large_lato_font_regular = ImageFont.load_default()

    # Defining information for requesting data
    randomPage = random.randint(0, 132680)
    BASE_URL = f"https://api.artic.edu/api/v1/artworks?page={randomPage}&limit=1&fields=title,artist_titles,image_id,description,date_display"
    artObject = {}
    try:
        response = requests.get(BASE_URL, timeout=10)

        # Chefcking if the request was succesful
        response.raise_for_status()

        # Parsing the data
        artObject = response.json()
        artObjectData = artObject["data"][0]
        print(artObjectData)
        artObjectConfig = artObject["config"]
        print(f"Loaded {artObjectData["title"]}")
        
    except requests.exceptions.requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as err:
        print(f"Error occurred: {err}")

    # If the art object has data, work with it
    if (artObject):

        # Trying to get the image file
        iiif_url = artObjectConfig.get("iiif_url")   # The museum's image server base URL
        image_id = artObjectData.get("image_id")
        IMAGE_URL = f"{iiif_url}/{image_id}/full/843,/0/default.jpg"
        
        image_response = requests.get(IMAGE_URL)
        if image_response.status_code == 200:
            filename = f"{image_id}_artic.jpg"
            with open(filename, "wb") as file:
                file.write(image_response.content)
            print(f"Saved image locally as {filename}")
        else:
            print("Failed to download the image file.")

