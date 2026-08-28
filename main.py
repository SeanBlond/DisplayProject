from PIL import Image, ImageDraw, ImageFont
import WeatherWindow
import ArtWindow
import SpotifyWindow
from dotenv import load_dotenv
import base64
import requests
import json
import os

# Trying to import inky stuff
try:
    from inky.auto import auto

    # Creating the inky display object
    inky_display = auto(ask_user=True, verbose=True)

    print("Inky succesfully loaded")
except:
    print("Failed to load Inky library")

# Creating the color palette
try:
    COLOR_PALETTE = {
        "BLACK": inky_display.BLACK,
        "WHITE": inky_display.WHITE,
        "RED": inky_display.RED,
        "GREEN": inky_display.GREEN,
        "BLUE": inky_display.BLUE,
        "YELLOW": inky_display.YELLOW,
        "ORANGE": inky_display.ORANGE,
        "LIGHT_GREY": (200, 200, 200),
        "GREY": (122, 122, 122),
        "GOLD": (194, 156, 50),
    }
except:
    COLOR_PALETTE = {
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "RED": (255, 0, 0),
        "GREEN": (12, 92, 12),
        "BLUE": (47, 47, 181),
        "YELLOW": (255, 255, 0),
        "ORANGE": (255, 140, 0),
        "LIGHT_GREY": (200, 200, 200),
        "GREY": (125, 125, 125),
        "DARK_GREY": (75, 75, 75),
        "GOLD": (194, 156, 50),
    }

# Creating image and drawing device
image = Image.new("P", (480, 800), "white")
image = image.convert("RGBA")
draw = ImageDraw.Draw(image)

# Loading api key
load_dotenv()
WEATHER_API_KEY = os.getenv("MET_WEATHER_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Functions for getting the spotify api tokens
def getToken():
    # Converting the client info to encoded data objects
    authString = SPOTIFY_CLIENT_ID + ":" + SPOTIFY_CLIENT_SECRET
    encodedAuth = authString.encode("utf-8")
    basedAuth = str(base64.b64encode(encodedAuth), "utf-8")

    # Defining what info will be sent to the API to get the token
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + basedAuth,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = { "grant_type": "client_credentials" }

    # Trying to get token from API
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        jsonResult = json.loads(response.content)
        token = jsonResult["access_token"]
        return token

    except requests.exceptions.Timeout  as errt:
        print(f"Timeout error: {errt}")

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP error: {errh}")

    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")

# Running above function to get the token
SPOTIFY_TOKEN = getToken()

# Calling the different window functions
print("Draw Weather Window")
WeatherWindow.DrawWindow(draw, COLOR_PALETTE, WEATHER_API_KEY, 300)
#ArtWindow.DrawWindow(image, draw, COLOR_PALETTE, 300)
#print("Draw Art Window")
SpotifyWindow.DrawSingleWindow(image, draw, COLOR_PALETTE, SPOTIFY_TOKEN, 550)
print("Draw Spotify Single Window")
#SpotifyWindow.DrawRandomSingleWindow(image, draw, COLOR_PALETTE, SPOTIFY_TOKEN, 550)
#print("Draw Spotify Single Window")
SpotifyWindow.DrawMultiWindow(image, draw, COLOR_PALETTE, SPOTIFY_TOKEN, 800)
print("Draw Spotify Multi Window")

# Drawing lines between the different windows
draw.line((10, 300, 470, 300), fill=COLOR_PALETTE["BLACK"], width=2)
draw.line((10, 550, 470, 550), fill=COLOR_PALETTE["BLACK"], width=2)

# Saving the image
image.save("displayImage.png")

# Inky stuff
try:
    # Rotating the image to fit the display
    inkyImage = Image.new("P", (inky_display.width, inky_display.height), inky_display.WHITE)
    rotImage = image.rotate(90, expand=True)

    # Sending the rotated image to the inky display
    inky_display.set_image(rotImage)
    inky_display.show()
except:
    print("Failed to run Inky functions")