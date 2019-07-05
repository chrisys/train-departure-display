import os
import requests
import json

def loadDeparturesForStation(journeyConfig, appId, apiKey):
    if journeyConfig["departureStation"] == "":
        raise ValueError(
            "Please set the journey.departureStation property in config.json")

    if appId == "" or apiKey == "":
        raise ValueError(
            "Please complete the transportApi section of your config.json file")

    departureStation = journeyConfig["departureStation"]

    URL = f"http://transportapi.com/v3/uk/train/station/{departureStation}/live.json"

    PARAMS = {'app_id': appId,
              'app_key': apiKey,
              'calling_at': journeyConfig["destinationStation"]}

    r = requests.get(url=URL, params=PARAMS)

    data = r.json()

    for item in data["departures"]["all"]:
         item['origin_name'] = item['origin_name'].replace('International', 'Intl.')
         item['origin_name'] = item['origin_name'].replace('London', 'LDN')
         item['destination_name'] = item['origin_name'].replace('International', 'Intl.')
         item['destination_name'] = item['origin_name'].replace('London', 'LDN')

    if "error" in data:
        raise ValueError(data["error"])

    return data["departures"]["all"], data["station_name"]


def loadDestinationsForDeparture(timetableUrl):
    r = requests.get(url=timetableUrl)

    data = r.json()

    data['origin_name'] = data['origin_name'].replace('International', 'Intl.')

    for item in data["stops"]:
         item['station_name'] = item['station_name'].replace('International', 'Intl.')
         item['station_name'] = item['station_name'].replace('London', 'LDN')

    if "error" in data:
        raise ValueError(data["error"])

    return list(map(lambda x: x["station_name"], data["stops"]))[1:]
