import os
import re

def loadConfig():
    data = {
        "journey": {},
        "api": {}
    }

    data["refreshTime"] = int(os.getenv("refreshTime") or 30)
    data["screenRotation"] = int(os.getenv("screenRotation") or 2)
    data["screenBlankHours"] = os.getenv("screenBlankHours") or ""
    data["emulator"] = False
    if os.getenv("emulator") == "True":
        data["emulator"] = True    
    data["dualScreen"] = False
    if os.getenv("dualScreen") == "True":
        data["dualScreen"] = True
    data["hoursPattern"] = re.compile("^((2[0-3]|[0-1]?[0-9])-(2[0-3]|[0-1]?[0-9]))$")

    data["journey"]["departureStation"] = os.getenv("departureStation") or "STP"

    data["journey"]["destinationStation"] = os.getenv("destinationStation") or ""
    if data["journey"]["destinationStation"] == "null" or data["journey"]["destinationStation"] == "undefined":
        data["journey"]["destinationStation"] = ""

    data["journey"]["individualStationDepartureTime"] = False
    if os.getenv("individualStationDepartureTime") == "True":
        data["journey"]["individualStationDepartureTime"] = True

    data["journey"]["outOfHoursName"] = os.getenv("outOfHoursName") or "London Paddington"
    data["journey"]["stationAbbr"] = { "International": "Intl." }
    data["journey"]['timeOffset'] = os.getenv("timeOffset") or "0"
    data["journey"]["screen1Platform"] = os.getenv("screen1Platform")
    data["journey"]["screen2Platform"] = os.getenv("screen2Platform")

    if data["journey"]["screen1Platform"].isnumeric() != True:
        data["journey"]["screen1Platform"] = ""

    if data["journey"]["screen2Platform"].isnumeric() != True:
        data["journey"]["screen2Platform"] = ""

    data["api"]["apiKey"] = os.getenv("apiKey") or None
    data["api"]["operatingHours"] = os.getenv("operatingHours") or ""

    data["showDepartureNumbers"] = False
    if os.getenv("showDepartureNumbers") == "True":
        data["showDepartureNumbers"] = True

    return data
    