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
            "Please configure the departureStation environment variable")

    if appId == None or apiKey == None:
        raise ValueError(
            "Please configure the transportApi_appId and transportApi_apiKey environment variables")

    departureStation = journeyConfig["departureStation"]

    URL = f"http://transportapi.com/v3/uk/train/station/{departureStation}/live.json"

    PARAMS = {'app_id': appId,
              'app_key': apiKey,
              'calling_at': journeyConfig["destinationStation"]}

    r = requests.get(url=URL, params=PARAMS)
    
    if r.status_code != 200:
        raise ValueError("Server error when loading data from TransportAPI - check your key and appId")

    data = r.json()
    
    #apply abbreviations / replacements to station names (long stations names dont look great on layout)
    for item in data["departures"]["all"]:
        item['origin_name'] = abbrStation(journeyConfig, item['origin_name'])
        item['destination_name'] = abbrStation(journeyConfig, item['destination_name'])

    for item in list(data["departures"]["all"]):
        if journeyConfig['departurePlatform'] is not None:
            if item['platform'] != journeyConfig['departurePlatform']:
                # Remove this item if the platform does not match
                data["departures"]["all"].remove(item)

    if "error" in data:
        raise ValueError(data["error"])

    return data["departures"]["all"], data["station_name"]


def loadDestinationsForDeparture(journeyConfig, timetableUrl):
    r = requests.get(url=timetableUrl)

    if r.status_code != 200:
        raise ValueError("Server error when loading data from TransportAPI - check your key and appId")

    data = r.json()

    #apply abbreviations / replacements to station names (long stations names dont look great on layout)
    #see config file for replacement list
    foundDepartureStation = False

    for item in list(data["stops"]):
        if item['station_code'] == journeyConfig['departureStation']:
            foundDepartureStation = True

        if foundDepartureStation == False:
            data["stops"].remove(item)
            continue

        item['station_name'] = abbrStation(journeyConfig, item['station_name'])

    if "error" in data:
        raise ValueError(data["error"])

    departureDestinationList = list(map(lambda x: x["station_name"], data["stops"]))[1:]

    if len(departureDestinationList) == 1:
        departureDestinationList[0] = departureDestinationList[0] + ' only.'

    return departureDestinationList
