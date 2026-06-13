import re
from datetime import datetime, timezone

import requests

TFL_BASE_URL = "https://api.tfl.gov.uk"


def normalizeLineId(lineName):
    """Best-effort mapping from a display line name to TfL line id"""
    if not lineName:
        return ""
    cleaned = lineName.strip().lower()
    if cleaned.endswith(" line"):
        cleaned = cleaned[:-5].strip()
    return cleaned.replace(" ", "-")


def extractLineIds(journeyConfig, arrivals):
    """Choose relevant line ids for disruption lookups"""
    lineFilter = (journeyConfig.get("tubeLine") or "").strip().lower()
    lineIds = []

    for arrival in arrivals:
        lineName = (arrival.get("lineName") or "").strip().lower()
        if lineFilter and lineName != lineFilter:
            continue
        lineId = (arrival.get("lineId") or "").strip().lower()
        if lineId and lineId not in lineIds:
            lineIds.append(lineId)

    if not lineIds and lineFilter:
        fallback = normalizeLineId(lineFilter)
        if fallback:
            lineIds.append(fallback)

    return lineIds


def fetchTubeDisruptionMessage(journeyConfig, arrivals, appKey):
    """Fetch the first non-good-service status reason for the configured/active lines"""
    lineIds = extractLineIds(journeyConfig, arrivals)
    if not lineIds:
        return ""

    params = {}
    if appKey:
        params["app_key"] = appKey

    try:
        response = requests.get(
            TFL_BASE_URL + "/Line/" + ",".join(lineIds) + "/Status",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        lines = response.json()
    except (requests.RequestException, ValueError):
        return ""

    for line in lines:
        lineName = (line.get("name") or "").strip()
        for status in line.get("lineStatuses") or []:
            severity = (status.get("statusSeverityDescription") or "").strip()
            if severity.lower() == "good service":
                continue
            reason = (status.get("reason") or "").strip()
            if reason:
                # Keep this compact enough to remain readable on the OLED scroller.
                return reason[:220]
            if lineName and severity:
                return (lineName + ": " + severity)[:220]

    return ""


def removeBrackets(originalName):
    return re.split(r" \(", originalName)[0]


def cleanStationName(name):
    """Tidy up a TfL station/destination name for the display"""
    if name is None:
        return ""
    name = removeBrackets(name)
    # remove the trailing "Underground Station" / "Rail Station" / "DLR Station" suffix
    name = re.sub(r"\s+(Underground|Rail|DLR)?\s*Station$", "", name).strip()
    return name


def extractPlatform(platformName):
    """Pull a numeric platform out of a TfL platformName like 'Northbound - Platform 2'"""
    if not platformName:
        return None
    match = re.search(r"Platform\s+(\d+)", platformName, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def parseExpectedArrival(value):
    """Convert a TfL ISO8601 timestamp into a local HH:MM string"""
    if not value:
        return None
    # TfL returns e.g. '2026-06-08T14:32:05Z'
    try:
        cleaned = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # convert to the host's local time (set by the TZ env var)
    return dt.astimezone().strftime("%H:%M")


def formatMins(seconds):
    """Format a TfL timeToStation (seconds) as an Underground-style countdown"""
    if seconds is None:
        return ""
    mins = int(seconds // 60)
    if mins <= 0:
        return "Due"
    if mins == 1:
        return "1 min"
    return str(mins) + " mins"


def ProcessTubeArrivals(journeyConfig, arrivals):
    lineFilter = journeyConfig.get("tubeLine") or ""
    lineFilter = lineFilter.strip().lower()

    directionFilter = journeyConfig.get("tubeDirection") or ""
    directionFilter = directionFilter.strip().lower()

    departureStationName = journeyConfig.get("outOfHoursName") or ""

    if not arrivals:
        return None, departureStationName

    # use the station name reported by the API
    departureStationName = cleanStationName(arrivals[0].get("stationName")) or departureStationName

    # optionally filter to a single line (a stop can serve several lines)
    if lineFilter:
        arrivals = [a for a in arrivals if (a.get("lineName") or "").lower() == lineFilter]

    # optionally filter by direction, matching either the API direction value
    # ("inbound"/"outbound") or a compass word in the platform name ("westbound" etc.)
    if directionFilter:
        def matchesDirection(arrival):
            direction = (arrival.get("direction") or "").lower()
            platformName = (arrival.get("platformName") or "").lower()
            filter_lower = directionFilter.lower()
            
            # Direct matches first
            if filter_lower in platformName or filter_lower == direction:
                return True
            
            # Map compass directions to TfL's inbound/outbound API values
            if filter_lower in ["westbound", "west"]:
                return direction == "inbound"
            elif filter_lower in ["eastbound", "east"]:
                return direction == "outbound"
            elif filter_lower in ["northbound", "north"]:
                return direction == "outbound"
            elif filter_lower in ["southbound", "south"]:
                return direction == "inbound"
            
            return False
            
        arrivals = [a for a in arrivals if matchesDirection(a)]

    if not arrivals:
        return None, departureStationName

    # TfL predictions are frequency based; order by soonest to arrive
    arrivals = sorted(arrivals, key=lambda a: a.get("timeToStation", 0))

    Departures = []
    for arrival in arrivals:
        thisDeparture = {}

        # skip predictions with no usable arrival time
        if parseExpectedArrival(arrival.get("expectedArrival")) is None:
            continue

        # Underground-style countdown (e.g. "2 mins", "Due")
        thisDeparture["mins_display"] = formatMins(arrival.get("timeToStation"))

        platform = extractPlatform(arrival.get("platformName"))
        if platform is not None:
            thisDeparture["platform"] = platform

        # full platform name and live location for the scrolling status line
        thisDeparture["platform_name"] = (arrival.get("platformName") or "").strip()
        thisDeparture["current_location"] = (arrival.get("currentLocation") or "").strip()

        # prefer "towards" to keep branch info (e.g. "Morden via Bank"), falling
        # back to destinationName when it's empty (e.g. DLR / Overground / Elizabeth line)
        destinationName = cleanStationName(
            arrival.get("towards") or arrival.get("destinationName")
        )
        thisDeparture["destination_name"] = destinationName

        # the Underground exposes no calling points; kept only because the
        # shared rendering helpers expect this key to be present
        thisDeparture["calling_at_list"] = ""

        Departures.append(thisDeparture)

    if not Departures:
        return None, departureStationName

    return Departures, departureStationName


def fetchStationName(stopPointId, appKey):
    """Look up the friendly common name for a StopPoint (used when there are no arrivals)"""
    try:
        params = {}
        if appKey:
            params["app_key"] = appKey
        response = requests.get(
            TFL_BASE_URL + "/StopPoint/" + stopPointId,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return cleanStationName(data.get("commonName"))
    except (requests.RequestException, ValueError):
        return ""


def loadTubeDeparturesForStation(journeyConfig, appKey, rows):
    if journeyConfig["departureStation"] == "":
        raise ValueError(
            "Please configure the departureStation environment variable")

    stopPointId = journeyConfig["departureStation"]

    params = {}
    if appKey:
        params["app_key"] = appKey

    response = requests.get(
        TFL_BASE_URL + "/StopPoint/" + stopPointId + "/Arrivals",
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    arrivals = response.json()

    disruptionMessage = fetchTubeDisruptionMessage(journeyConfig, arrivals, appKey)

    Departures, departureStationName = ProcessTubeArrivals(journeyConfig, arrivals)

    if not departureStationName:
        departureStationName = fetchStationName(stopPointId, appKey) or journeyConfig.get("outOfHoursName") or ""

    if Departures is None:
        return None, departureStationName, disruptionMessage

    try:
        maxRows = int(rows)
    except (TypeError, ValueError):
        maxRows = len(Departures)

    return Departures[:maxRows], departureStationName, disruptionMessage
