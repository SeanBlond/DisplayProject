from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO
import requests
import json

def DrawWindow(displayImage, draw, COLOR_PALETTE, API_TOKEN, startingYPos):
    # Loading fonts
    try:
        small_lato_font_regular = ImageFont.truetype("Lato/Lato-Bold.ttf", size=13)
        medium_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=20)
        medium_lato_font_bold = ImageFont.truetype("Lato/Lato-Bold.ttf", size=25)
    except IOError:
        small_lato_font_regular = ImageFont.load_default()
        medium_lato_font_regular = ImageFont.load_default()
        medium_lato_font_bold = ImageFont.load_default()

    
    # Defining function for getting the authorisation header
    def getAuthHeader(token):
        return {"Authorization": "Bearer " + token}

    # Getting the current date
    todaysDate = datetime.now()

    # Getting release data from the json file
    with open('releaseCalendar.json', 'r', encoding='utf-8') as file:
        possibleReleases = json.load(file)[todaysDate.strftime("%m-%d")]

    if (len(possibleReleases) == 0):
        print("No releases on todays date :(")
        return

    # Getting the release to display today
    todaysRelease = possibleReleases[0]
    for release in possibleReleases:
        if (release["release"]["weight"] > todaysRelease["release"]["weight"]):
            todaysRelease = release

    # Getting info on the release form the spotify API
    BASE_URL = f"https://api.spotify.com/v1/albums/{todaysRelease["release"]["release_id"]}?locale=en-US"

    # Requesting the data
    response = requests.get(BASE_URL, headers=getAuthHeader(API_TOKEN))
    
    if response.status_code == 429:
        # Get the header (default to 5 seconds if not found)
        retry_after = int(response.headers.get("Retry-After", 5))
        print(f"Rate limited! Waiting for {retry_after} seconds.")
        return
    
    # Loading the data for the output
    releaseResult = json.loads(response.content)
    yearsAgo = todaysDate.year - todaysRelease["release"]["release_year"]
    releaseName = releaseResult["name"]
    artistName = releaseResult["artists"][0]["name"]
    releaseDate = releaseResult["release_date"]
    releaseType = releaseResult["album_type"].capitalize()

    # Getting the image
    releaseImageURL = releaseResult["images"][0]["url"]
    releaseImageURLResposne = requests.get(releaseImageURL)
    releaseImage = Image.open(BytesIO(releaseImageURLResposne.content))
    releaseImage = releaseImage.resize((180, 180))
    releaseImage = releaseImage.convert("RGBA")

    # Drawing the release title to the screen
    draw.text((10, startingYPos - 240), f"Released {yearsAgo} years ago,", fill=COLOR_PALETTE["BLACK"], font=medium_lato_font_regular, anchor="lt")
    draw.text((10, startingYPos - 219), releaseName, fill=COLOR_PALETTE["BLACK"], font=medium_lato_font_bold, anchor="lt")
    
    # Drawing the outline and the image
    draw.rectangle((8, startingYPos - 192, 191, startingYPos - 9), fill=COLOR_PALETTE["BLACK"])
    displayImage.paste(releaseImage, (10, startingYPos - 190))

    # Drawing some release info
    draw.text((195, startingYPos - 190), f"Artist: {artistName}",    fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="lt")
    draw.text((195, startingYPos - 175), f"Released: {releaseDate}", fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="lt")
    draw.text((195, startingYPos - 160), f"Tracks:", fill=COLOR_PALETTE["BLACK"],                 font=small_lato_font_regular, anchor="lt")

    # Drawing info on each of the tracks of the release (max 8)
    releaseTracks = releaseResult["tracks"]["items"]
    for index, track in enumerate(releaseTracks):
        # Calculating yPos
        yPos = startingYPos - (145 - (index * 15))

        # Checking if the max index has been reached
        if (index > 8 and len(releaseTracks) > 8):
            draw.text((205, yPos + 2), "...", fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="lt")
            break

        # Drawing the track
        draw.text((205, yPos), f"-{track["name"]}", fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="lt")