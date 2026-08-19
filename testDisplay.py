from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import requests
import sys
import os

# Trying to import inky stuff
try:
    from inky.auto import auto
    print("Inky succesfully loaded")
except:
    print("Failed to load Inky library")

# Creating image and drawing device
image = Image.new("P", (480, 800), "white")
draw = ImageDraw.Draw(image)

# Loading fonts
try:
    small_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=15)
    symbol_font = ImageFont.truetype("easy_weather_icons_font/easy_weather_icons_font.ttf", size=35)
except IOError:
    small_lato_font_regular = ImageFont.load_default()
    symbol_font = ImageFont.load_default()

# Getting weather api ket
load_dotenv()
WEATHER_API_KEY = os.getenv("MET_WEATHER_KEY")

def DrawWeatherGraph(startingYPos):

    # Defining information for requesting data
    BASE_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly"
    HEADERS = {
        "apikey" : WEATHER_API_KEY,
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
        return

    # Drawing the background
    draw.rectangle(
        (0, startingYPos - 200, 480, startingYPos),
        fill=(99, 151, 235))

    # Getting the current date and allowed tomorrow date
    dundeeTime = datetime.now(ZoneInfo("Europe/London")) + timedelta(days=1)
    allowedFutureDate = (dundeeTime + timedelta(days=1)).replace(hour=0)

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
        timeString = dateTimeObject.strftime("%#H").lower()

        # Only draw the data if the hour is even
        if (dateTimeObject.hour % 2 == 0):
            # Drawing weather condition symbol
            draw.text(((index + 0.5) * 37, startingYPos - 20), WEATHER_CODE_SYMBOLS[entry["significantWeatherCode"]], fill=(255, 255, 255), font=symbol_font, anchor="ms")

            # Drawing time
            draw.text(((index + 0.5) * 37, startingYPos - 5), timeString, fill=(255, 255, 255), font=small_lato_font_regular, anchor="ms")

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
        (20, startingYPos - 190, 460, startingYPos - 60),
        fill=(80, 118, 212)
    )

    # Drawing incremental lines for each integer degree value
    degrees = int(round(maxGraphTemp) - round(minGraphTemp))
    degreeOffset = 130 / float(degrees)
    for i in range(degrees):
        lineYPos = startingYPos - 60 - (i * degreeOffset)
        draw.line((20, lineYPos, 460, lineYPos), fill=(37, 73, 161), width=1)

    # Drawing lines and labels for the top and bottom lines
    draw.text((18, startingYPos - 60), str(round(minGraphTemp)), fill=(255, 255, 255), font=small_lato_font_regular, anchor="rb")
    draw.text((18, startingYPos - 190), str(round(maxGraphTemp)), fill=(255, 255, 255), font=small_lato_font_regular, anchor="rt")
    draw.line((20, startingYPos - 60, 460, startingYPos - 60), fill=(255, 255, 255), width=2)
    draw.line((20, startingYPos - 190, 460, startingYPos - 190), fill=(255, 255, 255), width=2)

    # Looping through the temp data points and drawing a graph
    for i in range(len(actualTempPoints) - 1):
        # Calculating the line coords for the actual temperature
        actualTempLineStart = (i * 18.333 + 20, (actualTempPoints[i] - minGraphTemp) / tempGraphHeight * -120 + startingYPos - 65)
        actualTempLineEnd = ((i + 1) * 18.333 + 20, (actualTempPoints[i + 1] - minGraphTemp) / tempGraphHeight * -120 + startingYPos - 65)

        # Calculating the line coords for the feels like temperature
        feelsLikeTempLineStart = (i * 18.333 + 20, (feelsLikeTempPoints[i] - minGraphTemp) / tempGraphHeight * -120 + startingYPos - 65)
        feelsLikeTempLineEnd = ((i + 1) * 18.333 + 20, (feelsLikeTempPoints[i + 1] - minGraphTemp) / tempGraphHeight * -120 + startingYPos - 65)

        # Drawing a line from point i to i + 1
        draw.line((feelsLikeTempLineStart, feelsLikeTempLineEnd), fill=(200, 200, 200), width=3)
        draw.line((actualTempLineStart, actualTempLineEnd), fill=(255, 255, 255), width=3)

# Drawing the weather graph
DrawWeatherGraph(800)

# Saving the image
image.save("testImage.png")

#Inky stuff
try:
    #Creating the inky display object
    inky_display = auto(ask_user=True, verbose=True)

    #Rotating the image to fit the display
    inkyImage = Image.new("P", (inky_display.width, inky_display.height), inky_display.WHITE)
    rotImage = image.rotate(90, expand=True)

    # Sending the rotated image to the inky display
    inky_display.set_image(rotImage)
    inky_display.show()
except:
    print("Failed to run inky functions")
