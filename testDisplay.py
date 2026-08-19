from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import sys

# Trying to import inky stuff
try:
    from inky.auto import auto
    print("Inky succesfully loaded")
except:
    print("Failed to load Inky library")

# Defining information for requesting data
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

# Defining the time series array that will contain the info for the display
timeSeriesList = [];

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

# Getting the current date and allowed tomorrow date
dundeeTime = datetime.now(ZoneInfo("Europe/London")) + timedelta(days=1)
allowedFutureDate = dundeeTime + timedelta(days=1)
allowedFutureDate = allowedFutureDate.replace(hour=0)

# Defining members for keeping track of temp data for the graph
maxGraphTemp = max(timeSeriesList[0]["screenTemperature"], timeSeriesList[0]["feelsLikeTemperature"])
minGraphTemp = min(timeSeriesList[0]["screenTemperature"], timeSeriesList[0]["feelsLikeTemperature"])
maxTemp = timeSeriesList[0]["screenTemperature"]
minTemp = timeSeriesList[0]["screenTemperature"]
actualTempPoints = []
feelsLikeTempPoints = []

# Looping through each time series data point
index = 0;
for entry in timeSeriesList:
    # Getting time data
    dateTimeObject = datetime.strptime(entry["time"], "%Y-%m-%dT%H:%S%z")

    # If the date doesn't equal the current date, skip (except for allowed future date)
    if (dateTimeObject.date() != dundeeTime.date() and 
        (dateTimeObject.date() != allowedFutureDate.date() or
        dateTimeObject.hour != allowedFutureDate.hour)):
        continue

    # Calculating time
    timeString = dateTimeObject.strftime("%#I%p").lower()

    # Only draw the data if the hour is even
    if (dateTimeObject.hour % 2 == 0):
        # Drawing time
        draw.text(((index + 0.5) * 61.5, 390), timeString, fill=(0, 0, 0), font=lato_font_bold, anchor="ms")

        # Drawing weather condition symbol
        draw.text(((index + 0.5) * 61.5, 430), WEATHER_CODE_SYMBOLS[entry["significantWeatherCode"]], fill=(0, 0, 0), font=symbol_font, anchor="ms")

        # Drawing temps
        draw.text(((index + 0.5) * 61.5, 450), str(round(entry["screenTemperature"], 1)), fill=(0, 0, 0), font=lato_font_bold, anchor="ms")
        draw.text(((index + 0.5) * 61.5, 475), str(round(entry["feelsLikeTemperature"], 1)), fill=(100, 100, 100), font=lato_font_regular, anchor="ms")

        # Increasing index
        index += 1

    # Adding the temperature data points
    actualTempPoints.append(entry["screenTemperature"])
    feelsLikeTempPoints.append(entry["feelsLikeTemperature"])

    # Updating max/min temps
    maxGraphTemp = max(maxTemp, max(entry["screenTemperature"], entry["feelsLikeTemperature"]))
    minGraphTemp = min(minTemp, min(entry["screenTemperature"], entry["feelsLikeTemperature"]))
    maxTemp = max(maxTemp, entry["screenTemperature"])
    minTemp = min(minTemp, entry["screenTemperature"])

# Drawing a box for the temp graph
tempGraphHeight = max(maxGraphTemp - minGraphTemp, 5)
draw.rectangle(
    (30, 300, 770, 360),
    fill=(200, 200, 200)
)
draw.text((25, 360), str(round(minGraphTemp)), fill=(0, 0, 0), font=lato_font_regular, anchor="rb")
draw.text((25, 300), str(round(maxGraphTemp)), fill=(0, 0, 0), font=lato_font_regular, anchor="rt")
draw.line((30, 360, 770, 360), fill=(0, 0, 0), width=2)
draw.line((30, 300, 770, 300), fill=(0, 0, 0), width=2)

# Looping through the temp data points and drawing a graph
for i in range(len(actualTempPoints) - 1):
    # Calculating the line coords for the actual temperature
    actualTempLineStart = (i * 30.833 + 30.75, (actualTempPoints[i] - minGraphTemp) / tempGraphHeight * -50 + 355)
    actualTempLineEnd = ((i + 1) * 30.833 + 30.75, (actualTempPoints[i + 1] - minGraphTemp) / tempGraphHeight * -50 + 355)

    # Calculating the line coords for the feels like temperature
    feelsLikeTempLineStart = (i * 30.833 + 30.75, (feelsLikeTempPoints[i] - minGraphTemp) / tempGraphHeight * -50 + 355)
    feelsLikeTempLineEnd = ((i + 1) * 30.833 + 30.75, (feelsLikeTempPoints[i + 1] - minGraphTemp) / tempGraphHeight * -50 + 355)

    # Drawing a line from point i to i + 1
    draw.line((feelsLikeTempLineStart, feelsLikeTempLineEnd), fill=(100, 100, 100), width=3)
    draw.line((actualTempLineStart, actualTempLineEnd), fill=(0, 0, 0), width=3)


# Saving the image
image.save("testImage.png")

# Saving & showing the image
try:
    inky_display = auto(ask_user=True, verbose=True)
    inky_display.set_image(image)
    inky_display.show()
except:
    print("Failed to run inky functions")