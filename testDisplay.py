from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import requests
import sys

BASE_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly"
HEADERS = {
    "apikey" : open('api_key', 'r').read(),
    "accept" : "applications"
}
PARAMS = {
    "latitude": "56.462002",
    "longitude": "-2.970700",
    "excludeParameterMetadata": "true",
    "includeLocationName": "true"
}

# Arrays for weather codes
WEATHER_CODE_DESCRIPTIONS = {
    0:  "Clear Night", 
    1:  "Sunny Day",
    2:  "Partly Cloudy (night)",
    3:  "Partly Cloudy (day)",
    4:  "Not Used",
    5:  "Mist",
    6:  "Fog",
    7:  "Cloudy",
    8:	"Overcast",
    9:	"Light rain shower (night)",
    10:	"Light rain shower (day)",
    11:	"Drizzle",
    12:	"Light rain",
    13:	"Heavy rain shower (night)",
    14:	"Heavy rain shower (day)",
    15:	"Heavy rain",
    16:	"Sleet shower (night)",
    17:	"Sleet shower (day)",
    18:	"Sleet",
    19:	"Hail shower (night)",
    20:	"Hail shower (day)",
    21:	"Hail",
    22:	"Light snow shower (night)",
    23:	"Light snow shower (day)",
    24:	"Light snow",
    25:	"Heavy snow shower (night)",
    26:	"Heavy snow shower (day)",
    27:	"Heavy snow",
    28:	"Thunder shower (night)",
    29:	"Thunder shower (day)",
    30:	"Thunder"
}
WEATHER_CODE_SYMBOLS = {
    0 :  "",  # Clear Night
    1 :  "",  # Sunny Day
    2 :  "",  # Partly Cloudy (night)
    3 :  "",  # Partly Cloudy (day)
    4 :  "",  # Not Used
    5 :  "",  # Mist
    6 :  "",  # Fog
    7 :  "",  # Cloudy
    8 :  "",  # Overcast
    9 :  "",  # Light rain shower (night)
    10 : "",  # Light rain shower (day)
    11 : "",  # Drizzle
    12 : "",  # Light rain
    13 : "",  # Heavy rain shower (night)
    14 : "",  # Heavy rain shower (day)
    15 : "",  # Heavy rain
    16 : "",  # Sleet shower (night)
    17 : "",  # Sleet shower (day)
    18 : "",  # Sleet
    19 : "",  # Hail shower (night)
    20 : "",  # Hail shower (day)
    21 : "",  # Hail
    22 : "",  # Light snow shower (night)
    23 : "",  # Light snow shower (day)
    24 : "",  # Light snow
    25 : "",  # Heavy snow shower (night)
    26 : "",  # Heavy snow shower (day)
    27 : "",  # Heavy snow
    28 : "",  # Thunder shower (night)
    29 : "",  # Thunder shower (day)
    30 : ""   # Thunder
}

timeSeriesList = [];

# def kelvin_to_celsius(kelvin) :
#     return (kelvin - 273.15)

# def kelvin_to_farenheit(kelvin) :
#     return (kelvin - 273.15) * (9/5) + 32


# Getting the info from the API
try:
    response = requests.get(BASE_URL, headers=HEADERS, params=PARAMS, timeout=10)

    # Chefcking if the request was succesful
    response.raise_for_status()

    # Parsing the data
    weather_data = response.json()
    print("Succesfully read API data located at", weather_data["features"][0]["properties"]["location"]["name"])
    timeSeriesList = weather_data["features"][0]["properties"]["timeSeries"];

except requests.exceptions.requests.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")

except Exception as err:
    print(f"Error occurred: {err}")


# Looping through each time if applicable
if (len(timeSeriesList) == 0):
    sys.exit(0)


# Creating image and drawing device
image = Image.new("P", (800, 480), "white")
draw = ImageDraw.Draw(image)

# Loading font
try:
    lato_font_bold = ImageFont.truetype("Lato/Lato-Bold.ttf", size=20)
    lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=20)
    symbol_font = ImageFont.truetype("easy_weather_icons_font/easy_weather_icons_font.ttf", size=40)
except IOError:
    lato_font_large = ImageFont.load_default()
    lato_font_small = ImageFont.load_default()
    symbol_font = ImageFont.load_default()

# Drawing stuff to the image
# draw.rectangle((50, 50, 200, 200), fill=(255, 255, 0))  # Rectangle
# draw.ellipse((150, 150, 300, 300), fill=(255, 0, 0))  # Circle (ellipse)
# draw.line((0, 0, 400, 400), fill=(0, 0, 255), width=10)  # Diagonal line
# draw.text((0, 0), "Today in music history:", fill=(0, 0, 0), font=lato_font)
# draw.text((0, 40), "", fill=(0, 0, 0), font=symbol_font)

for index, entry in enumerate(timeSeriesList):
    dateTimeObject = datetime.strptime(entry["time"], "%Y-%m-%dT%H:%S%z")
    timeString = dateTimeObject.strftime("%I:%M %p")
    draw.text((index * 50, 200), WEATHER_CODE_SYMBOLS[entry["significantWeatherCode"]], fill=(0, 0, 0), font=symbol_font)
    draw.text((index * 50, 240), str(round(entry["screenTemperature"], 1)), fill=(0, 0, 0), font=lato_font_bold)
    draw.text((index * 50, 265), str(round(entry["feelsLikeTemperature"], 1)), fill=(100, 100, 100), font=lato_font_regular, )

# Saving & showing the image
image.save("testImage.png")
image.show()