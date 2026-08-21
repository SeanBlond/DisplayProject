from PIL import Image, ImageDraw, ImageFont
import WeatherWindow
#import ArtWindow
import SpotifyWindow
from dotenv import load_dotenv
import base64
import requests
import json
import os

# Trying to import inky stuff
try:
    from inky.auto import auto
    print("Inky succesfully loaded")
except:
    print("Failed to load Inky library")


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
WeatherWindow.DrawWindow(draw, WEATHER_API_KEY, 300)
#ArtWindow.DrawWindow(draw, 550)
SpotifyWindow.DrawWindow(image, draw, SPOTIFY_TOKEN, 550)

# Saving the image
image.save("displayImage.png")

#Inky stuff
try:
    # Creating the inky display object
    inky_display = auto(ask_user=True, verbose=True)

    # Rotating the image to fit the display
    inkyImage = Image.new("P", (inky_display.width, inky_display.height), inky_display.WHITE)
    rotImage = image.rotate(90, expand=True)

    # Sending the rotated image to the inky display
    inky_display.set_image(rotImage)
    inky_display.show()
except:
    print("Failed to run inky functions")