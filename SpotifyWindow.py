from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from io import BytesIO
import random
import requests
import json

def getAlbumFromID(id, authHeader):
    # Getting info on the release form the spotify API
    BASE_URL = f"https://api.spotify.com/v1/albums/{id}?locale=en-US"

    # Requesting the data
    response = requests.get(BASE_URL, headers=authHeader)

    if response.status_code == 429:
        # Get the header (default to 5 seconds if not found)
        retry_after = int(response.headers.get("Retry-After", 5))
        print(f"Rate limited! Waiting for {retry_after} seconds.")
        return

    return json.loads(response.content)

def getImageFromURL(imageURL, size):
    # Getting the image
    imageURLResposne = requests.get(imageURL)
    image = Image.open(BytesIO(imageURLResposne.content))
    image = image.resize(size)
    image = image.convert("RGBA")

    return image

def DrawSingleWindow(displayImage, draw, COLOR_PALETTE, API_TOKEN, startingYPos):
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

    # Getting the album from the Spotify API
    releaseResult = getAlbumFromID(todaysRelease["release"]["release_id"], getAuthHeader(API_TOKEN))

    # Getting release info
    yearsAgo = todaysDate.year - todaysRelease["release"]["release_year"]
    releaseName = releaseResult["name"]
    artistName = releaseResult["artists"][0]["name"]
    releaseDate = releaseResult["release_date"]
    releaseType = releaseResult["album_type"].capitalize()

    # Getting the image
    releaseImage = getImageFromURL(releaseResult["images"][0]["url"], (180, 180))

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

def DrawMultiWindow(displayImage, draw, COLOR_PALETTE, API_TOKEN, startingYPos):
    # Loading fonts
    try:
        small_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=13)
    except IOError:
        small_lato_font_regular = ImageFont.load_default()

    # Defining function for getting the authorisation header
    def getAuthHeader(token):
        return {"Authorization": "Bearer " + token}

    # Getting the current date
    todaysDate = datetime.now()

    # Getting release data from the json file
    with open('releaseCalendar.json', 'r', encoding='utf-8') as file:
        possibleReleases = json.load(file)[todaysDate.strftime("%m-%d")]

    if len(possibleReleases) == 0:
        print("No releases on todays date :(")
        return

    # Getting a list of the releases to display today
    todaysReleases = [possibleReleases[0]]
    for possibleRelease in possibleReleases[1:]:
        foundSpot = False
        for index, comparativeRelease in enumerate(todaysReleases):
            if possibleRelease["release"]["weight"] > comparativeRelease["release"]["weight"]:
                todaysReleases.insert(index, possibleRelease)
                foundSpot = True
                break

        if not foundSpot:
            todaysReleases.append(possibleRelease)


    # Looping through each possible release and displaying it to the image
    amountOfReleases = min(len(todaysReleases), 8)
    for i in range(amountOfReleases):
        # Defining drawing positions
        yPos = startingYPos - 250 + (int(i / 4) * 125) + 5 + (60 if amountOfReleases <= 4 else 0)
        if i < 4:
            amountInRow = 4 if amountOfReleases > 4 else amountOfReleases
        else:
            amountInRow = amountOfReleases - (4 * int(i / 4))
        xOffset = -58 * amountInRow + 248
        xPos = (i % 4 * 100) + (i % 4 * 16) + xOffset

        # Getting the album from the Spotify API
        releaseResult = getAlbumFromID(todaysReleases[i]["release"]["release_id"], getAuthHeader(API_TOKEN))

        # Getting release info
        artistName = releaseResult["artists"][0]["name"]

        # Getting the image
        releaseImage = getImageFromURL(releaseResult["images"][0]["url"], (100, 100))

        # Drawing info to the screen
        displayImage.paste(releaseImage, (int(xPos), int(yPos)))
        draw.text((xPos + 50, yPos + 105), artistName, fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="mt")

def DrawRandomSingleWindow(displayImage, draw, COLOR_PALETTE, API_TOKEN, startingYPos):
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

    # Setting the random seed based on todays date
    print(todaysDate.timetuple().tm_yday)
    random.seed(todaysDate.timetuple().tm_yday)

    # Getting a random index for the song
    songIndex = random.randrange(0, 550)

    # Defining the API URL to use
    BASE_URL = f"https://api.spotify.com/v1/me/top/tracks?time_range=medium_term&limit=1&offset={songIndex}"

    # Getting info from the API
    response = requests.get(BASE_URL, headers=getAuthHeader(API_TOKEN))

    if response.status_code == 429:
        # Get the header (default to 5 seconds if not found)
        retry_after = int(response.headers.get("Retry-After", 5))
        print(f"Rate limited! Waiting for {retry_after} seconds.")
        return

    trackResult = json.loads(response.content)
    print(trackResult)

    # Getting track info
    trackName = trackResult["name"]
    artistName = trackResult["artists"][0]["name"]
    trackDate = trackResult["track_date"]
    trackType = trackResult["album_type"].capitalize()

    # Getting the image
    trackImage = getImageFromURL(trackResult["images"][0]["url"], (180, 180))

    # Drawing the track title to the screen
    draw.text((10, startingYPos - 240), trackName, fill=COLOR_PALETTE["BLACK"], font=medium_lato_font_bold,
              anchor="lt")

    # Drawing the outline and the image
    draw.rectangle((8, startingYPos - 192, 191, startingYPos - 9), fill=COLOR_PALETTE["BLACK"])
    displayImage.paste(trackImage, (10, startingYPos - 190))

    # Drawing some track info
    draw.text((195, startingYPos - 190), f"Artist: {artistName}", fill=COLOR_PALETTE["BLACK"],
              font=small_lato_font_regular, anchor="lt")
    draw.text((195, startingYPos - 175), f"Released: {trackDate}", fill=COLOR_PALETTE["BLACK"],
              font=small_lato_font_regular, anchor="lt")
    draw.text((195, startingYPos - 160), f"Tracks:", fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular,
              anchor="lt")

    # Drawing info on each of the tracks of the track (max 8)
    trackTracks = trackResult["tracks"]["items"]
    for index, track in enumerate(trackTracks):
        # Calculating yPos
        yPos = startingYPos - (145 - (index * 15))

        # Checking if the max index has been reached
        if (index > 8 and len(trackTracks) > 8):
            draw.text((205, yPos + 2), "...", fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="lt")
            break

        # Drawing the track
        draw.text((205, yPos), f"-{track["name"]}", fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular,
                  anchor="lt")