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
    # Defining info used to request API data
    url = f"https://api.spotify.com/v1/artists/{artistID}/albums"
    headers = getAuthHeader(token)
    params = { 
        "limit": 10,
        "include_groups": "album"
    }


    # Requesting the data
    response = requests.get(url, headers=headers, params=params)
    jsonResult = json.loads(response.content)["items"]

    # Returning None if there are no artists
    if (len(jsonResult) == 0):
        print(f"No Albums found by artist: {artistID}")
        return None

    # Returning the albums
    return jsonResult

# Running above function to get the token
token = getToken()

artistID = "0epOFNiUfyON9EYx7Tpr6V"
albums = getAlbumsByArtist(token, artistID)
for album in albums:
    print(f"{album["name"]}: {album["release_date"]}")
