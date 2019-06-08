import os
import requests


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

    if "error" in data:
        raise ValueError(data["error"])

    return data["departures"]["all"], data["station_name"]


def loadDestinationsForDeparture(timetableUrl):
    r = requests.get(url=timetableUrl)

    data = r.json()

    if "error" in data:
        raise ValueError(data["error"])

    return list(map(lambda x: x["station_name"], data["stops"]))[1:]
