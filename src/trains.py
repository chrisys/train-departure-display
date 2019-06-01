import os
import requests


def loadDeparturesForStation(stationCode):
    TRANSPORT_APP_ID = os.environ["TRANSPORT_APP_ID"]
    TRANSPORT_API_KEY = os.environ["TRANSPORT_API_KEY"]

    if TRANSPORT_APP_ID == "" or TRANSPORT_API_KEY == "":
        raise ValueError(
            "Please set the 'TRANSPORT_APP_ID' and 'TRANSPORT_API_KEY' environment variables")

    URL = f"http://transportapi.com/v3/uk/train/station/{stationCode}/live.json"

    PARAMS = {'app_id': TRANSPORT_APP_ID,
              'app_key': TRANSPORT_API_KEY}

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
