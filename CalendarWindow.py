from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import calendar
from zoneinfo import ZoneInfo
import requests
import sys


def lerp(a, b, t):
    return t * a + (1 - t) * b;

def DrawCalendarWindow(draw, COLOR_PALETTE, startingYPos):
    # Loading fonts
    try:
        small_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=18)
        medium_lato_font_regular = ImageFont.truetype("Lato/Lato-Regular.ttf", size=24)
    except IOError:
        medium_lato_font_regular = ImageFont.load_default()
        small_lato_font_regular = ImageFont.load_default()

    # Getting the current date and first day of the month
    currentDay = datetime.now(ZoneInfo("Europe/London"))
    firstDay = currentDay.replace(day=1)

    # Drawing the name of the month
    draw.text((
        (3 * 25) + 20,
        startingYPos - 235
    ), firstDay.strftime("%B %Y"), fill=COLOR_PALETTE["BLACK"], font=medium_lato_font_regular, anchor="mt")

    # Drawing the weekday characters
    dayCharacters = ["M","T","W","T","F","S","S"]
    for index, character in enumerate(dayCharacters):
        draw.text((
            25 * index + 20,
            startingYPos - 200
        ), character, fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="mt")

    # Defining integers needed for the loop
    dayIndex = firstDay.weekday()
    amountOfDays = calendar.monthrange(firstDay.year, firstDay.month)[1]

    # Looping through each day and drawing its number
    for i in range(amountOfDays):
        datePosition = (
            25 * ((dayIndex + i) % 7) + 20,
            startingYPos - 170 + (25 * int((dayIndex + i) / 7))
        )

        # If the index is the current date, draw a red circle and white text
        if i + 1 == currentDay.day:
            circleBox = (
                datePosition[0] - 13,
                datePosition[1] - 13,
                datePosition[0] + 13,
                datePosition[1] + 13,
            )
            draw.ellipse(circleBox, fill=COLOR_PALETTE["RED"])
            draw.text(datePosition, str(i + 1), fill=COLOR_PALETTE["WHITE"], font=small_lato_font_regular, anchor="mm")

        else:
            draw.text(datePosition, str(i + 1), fill=COLOR_PALETTE["BLACK"], font=small_lato_font_regular, anchor="mm")

