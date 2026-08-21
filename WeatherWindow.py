from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import sys

def DrawWindow(draw, COLOR_PALETTE, API_KEY, startingYPos):
    # Loading fonts
    try:
        small_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=15)
        medium_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=28)
        large_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=36)
        symbol_font = ImageFont.truetype("easy_weather_icons_font/easy_weather_icons_font.ttf", size=35)
        large_symbol_font = ImageFont.truetype("easy_weather_icons_font/easy_weather_icons_font.ttf", size=48)
    except IOError:
        small_lato_font_regular = ImageFont.load_default()
        medium_lato_font_regular = ImageFont.load_default()
        large_lato_font_regular = ImageFont.load_default()
        large_symbol_font = ImageFont.load_default()
        symbol_font = ImageFont.load_default()

    # Getting the current date and allowed tomorrow date
    dundeeTime = datetime.now(ZoneInfo("Europe/London")) + timedelta(days=1)
    allowedFutureDate = (dundeeTime + timedelta(days=1)).replace(hour=0)

    # Getting daily weather info
    BASE_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/daily"
    HEADERS = {
        "apikey" : API_KEY,
        "accept" : "applications"
    }
    PARAMS = {
        "latitude": "56.462002",
        "longitude": "-2.970700",
        "excludeParameterMetadata": "true",
        "includeLocationName": "true"
    }

    # Getting the info from the API
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=PARAMS, timeout=10)

        # Chefcking if the request was succesful
        response.raise_for_status()

        # Parsing the data
        weather_data = response.json()

        # Looping through each day to check which one is the correct day
        weatherToday = {}
        for day in weather_data["features"][0]["properties"]["timeSeries"]:
            date = datetime.strptime(day["time"], "%Y-%m-%dT%H:%S%z")
            if (date.date() == dundeeTime.date()):
                weatherToday = day
                break

        # Drawing temp ranges
        tempRange = f"{round(weatherToday["dayUpperBoundMaxTemp"])}°C / {round(weatherToday["nightLowerBoundMinTemp"])}°C"
        feelsLikeTempRange = f"{round(weatherToday["dayUpperBoundMaxFeelsLikeTemp"])}°C / {round(weatherToday["nightLowerBoundMinFeelsLikeTemp"])}°C" 
        draw.text((240, startingYPos - (200 + 5)), tempRange, fill=COLOR_PALETTE["BLACK"], font=large_lato_font_regular, anchor="mb")
        draw.text((240, startingYPos - (200 - 3)), feelsLikeTempRange, fill=COLOR_PALETTE["LIGHT_GREY"], font=medium_lato_font_regular, anchor="mt")

        # Drawing chance of rain
        rainIcons = [
            "", # Nothing
            "", # Showers
            "", # Rain
            "", # Heavy Showers
        ]
        rainChance = f"{weatherToday["dayProbabilityOfPrecipitation"]}%"
        rainIconIndex = round((weatherToday["dayProbabilityOfPrecipitation"] / 25))
        draw.text((80, startingYPos - (200 + 3)), rainIcons[rainIconIndex], fill=COLOR_PALETTE["BLACK"], font=large_symbol_font, anchor="mb")
        draw.text((80, startingYPos - (200 - 3)), rainChance, fill=COLOR_PALETTE["LIGHT_GREY"], font=medium_lato_font_regular, anchor="mt")

        # Drawing wind speeds
        windSpeeds = f"{weatherToday["midday10MWindSpeed"]}"
        draw.text((400, startingYPos - (200 - 3)), "", fill=COLOR_PALETTE["BLACK"], font=large_symbol_font, anchor="mb")
        draw.text((400, startingYPos - (200 - 3)), windSpeeds, fill=COLOR_PALETTE["LIGHT_GREY"], font=medium_lato_font_regular, anchor="mt")

        # Drawing day at the top
        dateText = dundeeTime.strftime("%A, %B %#d, %Y")
        draw.text((240, startingYPos - 282), dateText, fill=COLOR_PALETTE["BLACK"], font=medium_lato_font_regular, anchor="mt")
        
        # Calculating the min and max temperature for the graph
        tempGraphMin = min(weatherToday["nightLowerBoundMinFeelsLikeTemp"], weatherToday["nightMinScreenTemperature"])
        tempGraphMax = max(weatherToday["dayUpperBoundMaxFeelsLikeTemp"], weatherToday["dayMaxScreenTemperature"])

    except requests.exceptions.requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as err:
        print(f"Error occurred: {err}")


    # Defining information for requesting hourly data
    BASE_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly"
    HEADERS = {
        "apikey" : API_KEY,
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
        0 :  "",  # Clear Night
        1 :  "",  # Sunny Day
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
        timeSeriesList = weather_data["features"][0]["properties"]["timeSeries"];

    except requests.exceptions.requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as err:
        print(f"Error occurred: {err}")

    # Looping through each time if applicable
    if (len(timeSeriesList) == 0):
        return

    # Defining members for keeping track of temp data for the graph
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
            draw.text(((index + 0.5) * 37, startingYPos - 20), WEATHER_CODE_SYMBOLS[entry["significantWeatherCode"]], fill=COLOR_PALETTE["BLACK"], font=symbol_font, anchor="ms")

            # Drawing time
            draw.text(((index + 0.5) * 37, startingYPos - 5), timeString, fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="ms")

            # Increasing index
            index += 1

        # Adding the temperature data points
        actualTempPoints.append(entry["screenTemperature"])
        feelsLikeTempPoints.append(entry["feelsLikeTemperature"])

    # Calculating the height of the graph
    tempGraphHeight = max(tempGraphMax - tempGraphMin, 5)

    # Drawing incremental lines for each integer degree value
    degrees = int(round(tempGraphMax) - round(tempGraphMin))
    degreeOffset = 100 / float(degrees)
    for i in range(degrees):
        lineYPos = startingYPos - 60 - (i * degreeOffset)
        draw.line((20, lineYPos, 460, lineYPos), fill=COLOR_PALETTE["BLACK"], width=1)

    # Drawing lines and labels for the top and bottom lines
    draw.text((18, startingYPos - 60), str(round(tempGraphMin)), fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="rb")
    draw.text((18, startingYPos - 160), str(round(tempGraphMax)), fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="rt")
    draw.line((20, startingYPos - 60, 460, startingYPos - 60), fill=COLOR_PALETTE["BLACK"], width=2)
    draw.line((20, startingYPos - 160, 460, startingYPos - 160), fill=COLOR_PALETTE["BLACK"], width=2)

    # Looping through the temp data points and drawing a graph
    for i in range(len(actualTempPoints) - 1):
        # Calculating the line coords for the actual temperature
        actualTempLineStart = (i * 18.333 + 20, (actualTempPoints[i] - tempGraphMin) / tempGraphHeight * -90 + startingYPos - 65)
        actualTempLineEnd = ((i + 1) * 18.333 + 20, (actualTempPoints[i + 1] - tempGraphMin) / tempGraphHeight * -90 + startingYPos - 65)

        # Calculating the line coords for the feels like temperature
        feelsLikeTempLineStart = (i * 18.333 + 20, (feelsLikeTempPoints[i] - tempGraphMin) / tempGraphHeight * -90 + startingYPos - 65)
        feelsLikeTempLineEnd = ((i + 1) * 18.333 + 20, (feelsLikeTempPoints[i + 1] - tempGraphMin) / tempGraphHeight * -90 + startingYPos - 65)

        # Drawing a line from point i to i + 1
        draw.line((feelsLikeTempLineStart, feelsLikeTempLineEnd), fill=COLOR_PALETTE["LIGHT_GREY"], width=3)
        draw.line((actualTempLineStart, actualTempLineEnd), fill=COLOR_PALETTE["BLACK"], width=3)
