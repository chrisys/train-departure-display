import os
import requests


def loadDeparturesForStation(stationCode, appId, apiKey):
    if stationCode == "":
        raise ValueError(
            "Please set the 'DEPARTURE_STATION_CODE' environment variable")

    if appId == "" or apiKey == "":
        raise ValueError(
            "Please set the 'TRANSPORT_APP_ID' and 'TRANSPORT_API_KEY' environment variables")

    URL = f"http://transportapi.com/v3/uk/train/station/{stationCode}/live.json"

    PARAMS = {'app_id': appId,
              'app_key': apiKey}

    r = requests.get(url=URL, params=PARAMS)

    data = r.json()

    if "error" in data:
        raise ValueError(data["error"])

    return data["departures"]["all"]


def loadDestinationsForDepartre(timetableUrl):
    r = requests.get(url=timetableUrl)

    data = r.json()

    if "error" in data:
        raise ValueError(data["error"])

    return list(map(lambda x: x["station_name"], data["stops"]))
