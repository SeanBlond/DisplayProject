from platform import release
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import random

def getRandomArt():
    # Defining information for requesting data
    randomPage = random.randint(0, 1000)
    BASE_URL = f"https://api.artic.edu/api/v1/artworks/search?query[term][artwork_type_id]=1&page={randomPage}&limit=1&fields=title,id,artist_titles,thumbnail,image_id,description,date_display"
    
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

def getArtImage(artID, urlBase, width=0, height=0):
    requestSize = ""
    if (width == 0 and height == 0):
        print("Invalid dimensions requested")
        return
    elif (width == 0):
        requestSize = f",{height}"
    elif (height == 0):
        requestSize = f"{width},"
    else:
        requestSize = f"{width},{height}"


    # Trying to get the image file
    IMAGE_URL = f"{urlBase}/{artID}/full/{requestSize}/0/default.jpg"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # Getting the image
    try:
        #Requesting the image url
        response = requests.get(IMAGE_URL, headers=headers, timeout=2)

        # Checking if the request was succesful
        response.raise_for_status()

        # Creating and returning the image
        artImage = Image.open(BytesIO(response.content))
        return artImage

    except:
        print("Failed to download the image file.")
        print(f"Status Code: {response.status_code}")
        return

def DrawWindow(displayImage, draw, COLOR_PALETTE, startingYPos):
    # Loading fonts
    try:
        lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=20)
        lato_font_bold = ImageFont.truetype("Lato/Lato-Bold.ttf", size=22)
    except IOError:
        lato_font_regular = ImageFont.load_default()
        lato_font_bold = ImageFont.load_default()

    # Getting a random art object
    artObject = getRandomArt()

    # If the art object was unreachable, exit
    if not artObject:
        return

    #print(artObject);

    # Determining the art object aspect ratio
    aspectRatio = artObject["data"][0]["thumbnail"]["width"] / artObject["data"][0]["thumbnail"]["height"]
    print(aspectRatio)

    # Defining stuff needed for getting the art image
    iiif_url = artObject["config"]["iiif_url"]
    image_id = artObject["data"][0]["image_id"]

    # Getting a different size image depending on the aspect ratio
    artImage = {}
    if (aspectRatio > 0.8):
        # Art is wider, request image with smaller height
        if (aspectRatio * 220 > 460):
            artImage = getArtImage(image_id, iiif_url, width=460)
        else:
            artImage = getArtImage(image_id, iiif_url, height=220)
    else: 
        # Art is thinner, request image with larger height
        artImage = getArtImage(image_id, iiif_url, height=280)

    if not artImage:
        return

    print(artObject["data"][0]["id"])

    # Defining text from the art object that will be drawn to the screen
    artTitle = artObject["data"][0]["title"]
    artistName = artObject["data"][0]["artist_titles"][0]
    releaseYear = artObject["data"][0]["date_display"]

    # Drawing the art image and info to the screen
    if (aspectRatio > 0.8):
        # Drawing the border
        paintingXPos = int((460 - artImage.width) / 2 + 10)
        draw.rounded_rectangle(
            (paintingXPos - 5, startingYPos - 295, paintingXPos + artImage.width + 4, startingYPos - 66),
            radius=3,
            fill=COLOR_PALETTE["GOLD"])

        # Drawing the artwork
        displayImage.paste(artImage, (paintingXPos, startingYPos - 290))

        # Drawing title, artist, and year
        draw.text((240, startingYPos - 60), artTitle, fill=COLOR_PALETTE["BLACK"], font=lato_font_bold, anchor="mt")
        draw.text((240, startingYPos - 35), f"{artistName} ({releaseYear})", fill=COLOR_PALETTE["DARK_GREY"], font=lato_font_regular, anchor="mt")

    else:
        # Drawing the border
        draw.rounded_rectangle(
            (5, startingYPos - 295, artImage.width + 14, startingYPos - 6),
            radius=3,
            fill=COLOR_PALETTE["GOLD"])

        # Drawing the artwork
        displayImage.paste(artImage, (10, startingYPos - 290))

        # Checking if the text to be drawn would exceed the window
        titleText = artTitle
        titleTextBox = draw.textbbox((artImage.width + 20, startingYPos - 290), titleText, font=lato_font_bold)
        if (titleTextBox[2] > 475):
            # Text to long, must resize
            for i in range(len(titleText)):
                splicedString = titleText[0:len(titleText) - i]
                newTextBox = draw.textbbox((artImage.width + 20, startingYPos - 290), splicedString, font=lato_font_bold)
                if (newTextBox[2] <= 475):
                    titleText = titleText[:len(titleText) - i - 1] + "-\n" + titleText[len(titleText) - i - 1:]
                    break

        artistText = f"{artistName} ({releaseYear})"
        artistTextYPos = draw.textbbox((artImage.width + 20, startingYPos - 290), titleText, font=lato_font_bold)
        artistTextBox = draw.textbbox((artImage.width + 20, artistTextYPos[3]), artistText, font=lato_font_regular)
        if (artistTextBox[2] > 475):
            # Text to long, must resize
            for i in range(len(artistText)):
                splicedString = artistText[0:len(artistText) - i]
                newTextBox = draw.textbbox((artImage.width + 20, startingYPos - 290), splicedString, font=lato_font_regular)
                if (newTextBox[2] <= 475):
                    artistText = artistText[:len(artistText) - i - 1] + "-\n" + artistText[len(artistText) - i - 1:]
                    break


        # Drawing title, artist, and year
        draw.text((artImage.width + 20, startingYPos - 290), titleText, fill=COLOR_PALETTE["BLACK"], font=lato_font_bold, anchor="la")
        draw.text((artImage.width + 20, artistTextYPos[3]), artistText, fill=COLOR_PALETTE["DARK_GREY"], font=lato_font_regular, anchor="la")


