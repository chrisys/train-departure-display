import os

def loadConfig():
    data = {
        "journey": {},
        "api": {}
    }

    data["refreshTime"] = int(os.getenv("refreshTime") or 180)
    data["screenRotation"] = int(os.getenv("screenRotation") or 2)
    data["screenBlankHours"] = os.getenv("screenBlankHours") or "1-6"

    data["journey"]["departureStation"] = os.getenv("departureStation") or "PAD"
    data["journey"]["destinationStation"] = os.getenv("destinationStation") or ""
    data["journey"]["outOfHoursName"] = os.getenv("outOfHoursName") or "London Paddington"
    data["journey"]["departurePlatform"] = os.getenv("departurePlatform") or None
    data["journey"]["stationAbbr"] = { "International": "Intl." }
    data["journey"]['timeOffset'] = os.getenv("screenRotation") or "0"

    data["api"]["apiKey"] = os.getenv("apiKey") or None
    data["api"]["operatingHours"] = os.getenv("operatingHours") or "8-22"

    return data