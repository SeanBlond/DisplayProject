from dotenv import load_dotenv
import requests
import base64
import json
import os

# Loading in API stuff from the .env file
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

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


def getAuthHeader(token):
    return {"Authorization": "Bearer " + token}

def searchForArtist(token, artistName):
    # Defining info used to request API data
    url = "https://api.spotify.com/v1/search"
    headers = getAuthHeader(token)
    query = f"q={artistName}&type=artist&limit=1"
    queryURL = url + "?" + query

    # Requesting the data
    response = requests.get(queryURL, headers=headers)
    jsonResult = json.loads(response.content)["artists"]["items"]

    # Returning None if there are no artists
    if (len(jsonResult) == 0):
        print(f"No Artist found with name: {artistName}")
        return None

    # Returning the first found artist
    return jsonResult[0]

def getAlbumsByArtist(token, artistID):
    albumList = []
    loopActive = True
    index = 0

    while loopActive:
        # Defining info used to request API data
        url = f"https://api.spotify.com/v1/artists/{artistID}/albums"
        headers = getAuthHeader(token)
        params = { 
            "limit": 10,
            "offset": index
            #"include_groups": "album"
        }

        # Requesting the data
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            # Get the header (default to 5 seconds if not found)
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited! Waiting for {retry_after} seconds.")

        jsonResult = json.loads(response.content)
        print(jsonResult)
        albumsInJson = json.loads(response.content)["items"]

        # loading in each album
        for album in albumsInJson:
            albumObject = {"id": album["id"], "release_date": album["release_date"]}
            albumList.append(albumObject)

        # Increasing index
        index += 10

        # Checking if the loop can be closed
        if (index > jsonResult["total"] or index >= 50):
            loopActive = False

    # Returning the albums
    return albumList

# Running above function to get the token
token = getToken()

artists = [
    "6FlOCziOXI157pvUREAh3E",
    "60YWN7EYUFUjIRTx0bX5Lj",
    "0vFpdm2mk6RPUlJrU5hDLY",
    "6p2HnfM955TI1bX34dkLnI",
    "4dAQ5VFw5nhwA6rTf3ENQ2",
    "6bVGMtAf6mPtO1LWxUg1y5",
    "0qmHQLCyJrgGFtqLDSRHJ4",
    "4JfHqFjyolUL4WIReuucSs",
    "5ictveRyhWRs8Gt8Dvt1hS",
    "38SKxCyfrmNWqWunb9wGHP",
    "6vCs4rj3rvYAX3l7dEiPq9",
    "5e4mQ2QunM3CN88XI65i7V",
    "1HxXNvsraqrsgfmju1yKk8",
    "5vh3TBzvI4nASt2A1KfgcR",
    "6RU2UUN1UIOWpP3aO6M70K",
    "5N5jf98OOEf3uAIJpi1deD",
    "69Kp4bE7aUWEPrmTwmhVZR",
    "3lWVgSwutPsiJ8Awm7OTKU",
    "0epOFNiUfyON9EYx7Tpr6V",
    "0NIPkIjTV8mB795yEIiPYL",
    "4aKWmkWAKviFlyvHYPTNQY",
    "7m5HFZUYErjDv6fblK43w3",
    "5h6KJPKB8cSVJTWZhKAZoT",
    "5Vd6nIpBPLzJDQDcvILQu4",
    "73rPcaYEhBd0UuVZBqqyQJ",
    "0lawSNBxNgJFQYJnQzLH8c",
    "7gW0r5CkdEUMm42w9XpyZO",
    "74KM79TiuVKeVCqs8QtB0B",
    "3uwUtL5kPSO2mpOhU4SiWz",
    "4DiZJ3Gg7B1EWeKoQO36Ae",
    "07VKGw5BhunkwMnvz71Z1h",
    "5YA1c6yVkPnflTLMfOgjzc"
]

exportJson = {}
for artist in artists:
    albums = getAlbumsByArtist(token, artist)
    print(f"Loaded artist {artist} with {len(albums)} albums")
    exportJson[artist] = albums

# Dumping the json
with open('output.json', 'w', encoding='utf-8') as file:
    json.dump(exportJson, file, indent=4)
