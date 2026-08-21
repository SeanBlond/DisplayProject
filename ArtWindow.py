from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import random

def getRandomArt():
    # Defining information for requesting data
    randomPage = random.randint(0, 1000)
    BASE_URL = f"https://api.artic.edu/api/v1/artworks/search?query[term][artwork_type_id]=1&page={randomPage}&limit=1&fields=title,artist_titles,image_id,description,date_display"
    
    artObject = {}
    try:
        response = requests.get(BASE_URL, timeout=2)

        # Chefcking if the request was succesful
        response.raise_for_status()

        # Parsing the data
        artObject = response.json()
        return artObject
        
    except requests.exceptions.requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as err:
        print(f"Error occurred: {err}")

def getArtImage(artID, urlBase):
    # Trying to get the image file
    IMAGE_URL = f"{urlBase}/{artID}/full/,240/0/default.jpg"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # Getting the image
    try:
        #Requesting the image url
        response = requests.get(IMAGE_URL, headers=headers, timeout=5)

        # Checking if the request was succesful
        response.raise_for_status()

        # Creating and returning the image
        artImage = Image.open(BytesIO(response.content))
        return artImage

    except:
        print("Failed to download the image file.")
        return

def DrawWindow(displayImage, draw, startingYPos):
    # Loading fonts
    try:
        small_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=15)
        medium_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=28)
        large_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=36)
    except IOError:
        small_lato_font_regular = ImageFont.load_default()
        medium_lato_font_regular = ImageFont.load_default()
        large_lato_font_regular = ImageFont.load_default()

    artObject = getRandomArt()

    # If the art object has data, work with it
    if (artObject):
        # Trying to get an image from the art object
        iiif_url = artObject["config"]["iiif_url"]
        image_id = artObject["data"][0]["image_id"]
        artImage = getArtImage(image_id, iiif_url)

        if not artImage:
            return

        # Drawing the art image to the screen
        displayImage.paste(artImage, (10, startingYPos - 300))

