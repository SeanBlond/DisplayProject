import json
from datetime import datetime

releaseCalendarFormat = {
    "08-27": [
        {
            "release": {
                "release_id": "6FlOCziOXI157pvUREAh3E",
                "release_year": 2025,
                "weight": 10,
            }
        }
    ],
    "04-03": [
        {
            "release": {
                "release_id": "7pGzGYHDOMvdyqY1RBzBjB",
                "release_year": 2026,
                "weight": 8,
            }
        }
    ],
}

# Loading in the json file
with open('artistReleases.json', 'r', encoding='utf-8') as file:
    releaseData = json.load(file)

# Looping through each artist
totalReleases = 0
releaseCalendar = {}
for artist in releaseData["artists"]:
    # Incrementing releases
    totalReleases += len(artist["releases"])

    # Looping through and storing each release
    for release in artist["releases"]:
        # Reading the date
        print(f"Reading date {release["release_date"]}")
        dateTimeObject = datetime.strptime(release["release_date"], "%Y-%m-%d")

        # Pushing the albulm data to the release claendar
        releaseDateKey = dateTimeObject.strftime("%m-%d")
        if releaseDateKey not in releaseCalendar:
            releaseCalendar[releaseDateKey] = [{
                "release": {
                    "release_id": release["id"],
                    "release_year": dateTimeObject.year,
                    "weight": artist["weight"],
                }
            }]
        else:
            releaseCalendar[releaseDateKey].append({
                "release": {
                    "release_id": release["id"],
                    "release_year": dateTimeObject.year,
                    "weight": artist["weight"],
                }
            })


    # Printing out the artist data
    print(f"Reading {len(artist["releases"])} releases from {artist["name"]}")

# Outputting total amount of releases:
print(f"Read a total of {totalReleases} releases")

# Dumping the json
with open('releaseCalendar.json', 'w', encoding='utf-8') as file:
    json.dump(releaseCalendar, file, indent=4)
