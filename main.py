from PIL import Image, ImageDraw, ImageFont
#import WeatherWindow
import ArtWindow
from dotenv import load_dotenv
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

# Loading api key
load_dotenv()
WEATHER_API_KEY = os.getenv("MET_WEATHER_KEY")

# Calling the different window functions
#WeatherWindow.DrawWeatherGraph(draw, WEATHER_API_KEY, 300)
ArtWindow.DrawArtWindow(draw, 550)

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