import os
import requests
import json

def abbrStation(journeyConfig, inputStr):
    dict = journeyConfig['stationAbbr']
    for key in dict.keys():
        inputStr = inputStr.replace(key, dict[key])
    return inputStr

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
    #apply abbreviations / replacements to station names (long stations names dont look great on layout)
    #see config file for replacement list 
    for item in data["departures"]["all"]:
         item['origin_name'] = abbrStation(journeyConfig, item['origin_name'])
         item['destination_name'] = abbrStation(journeyConfig, item['destination_name'])

    if "error" in data:
        raise ValueError(data["error"])

    return data["departures"]["all"], data["station_name"]


def loadDestinationsForDeparture(journeyConfig, timetableUrl):
    r = requests.get(url=timetableUrl)

    data = r.json()

    #apply abbreviations / replacements to station names (long stations names dont look great on layout)
    #see config file for replacement list 
    for item in data["stops"]:
         item['station_name'] = abbrStation(journeyConfig, item['station_name'])

    if "error" in data:
        raise ValueError(data["error"])

    return list(map(lambda x: x["station_name"], data["stops"]))[1:]

