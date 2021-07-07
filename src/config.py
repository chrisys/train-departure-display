import os

def loadConfig():
    data = {
        "journey": {},
        "transportApi": {}
    }

    data["refreshTime"] = int(os.getenv("refreshTime")) or 180

    data["journey"]["departureStation"] = os.getenv("departureStation") or "PAD"
    data["journey"]["destinationStation"] = os.getenv("destinationStation") or None
    data["journey"]["outOfHoursName"] = os.getenv("departureStation") or "London Paddington"
    data["journey"]["stationAbbr"] = { "International": "Intl." }

    data["transportApi"]["appId"] = os.getenv("transportApi_appId") or None
    data["transportApi"]["apiKey"] = os.getenv("transportApi_apiKey") or None
    data["transportApi"]["operatingHours"] = os.getenv("transportApi_operatingHours") or "0-23"

    return data