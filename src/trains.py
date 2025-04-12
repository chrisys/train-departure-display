import requests
import re
import xmltodict


def removeBrackets(originalName):
    return re.split(r" \(", originalName)[0]


def isTime(value):
    matches = re.findall(r"\d{2}:\d{2}", value)
    return len(matches) > 0


def joinwithCommas(listIN):
    return ", ".join(listIN)[::-1].replace(",", "dna ", 1)[::-1]


def removeEmptyStrings(items):
    return filter(None, items)


def joinWith(items, joiner: str):
    filtered_list = removeEmptyStrings(items)
    return joiner.join(filtered_list)


def joinWithSpaces(*args):
    return joinWith(args, " ")


def prepareServiceMessage(operator):
    return joinWithSpaces("A" if operator not in ['Elizabeth Line', 'Avanti West Coast'] else "An", operator, "Service")


def prepareLocationName(location, show_departure_time):
    location_name = removeBrackets(location['lt7:locationName'])

    if not show_departure_time:
        return location_name
    else:
        scheduled_time = location["lt7:st"]
        try:
            expected_time = location["lt7:et"]
        except KeyError:
            # as per api docs, it's 'at' if there isn't an 'et':
            expected_time = location["lt7:at"]
        departure_time = expected_time if isTime(expected_time) else scheduled_time
        formatted_departure = joinWith(["(", departure_time, ")"], "")
        return joinWithSpaces(location_name, formatted_departure)


def prepareCarriagesMessage(carriages):
    if carriages == 0:
        return ""
    else:
        return joinWithSpaces("formed of", carriages, "coaches.")


def ArrivalOrder(ServicesIN):
    ServicesOUT = []
    for servicenum, eachService in enumerate(ServicesIN):
        STDHour = int(eachService['lt4:std'][0:2])
        STDMinute = int(eachService['lt4:std'][3:5])
        if (STDHour < 2):
            STDHour += 24  # this prevents a 12am departure displaying before a 11pm departure
        STDinMinutes = STDHour * 60 + STDMinute  # this service is at this many minutes past midnight
        ServicesOUT.append(eachService)
        ServicesOUT[servicenum]['sortOrder'] = STDinMinutes
    ServicesOUT = sorted(ServicesOUT, key=lambda k: k['sortOrder'])
    return ServicesOUT


def ProcessDepartures(journeyConfig, APIOut):
    show_individual_departure_time = journeyConfig["individualStationDepartureTime"]
    APIElements = xmltodict.parse(APIOut)
    Services = []

    # get departure station name
    departureStationName = APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']['lt4:locationName']

    # if there are only train services from this station
    if 'lt7:trainServices' in APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']:
        Services = APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']['lt7:trainServices']['lt7:service']
        if isinstance(Services, dict):  # if there's only one service, it comes out as a dict
            Services = [Services]       # but it needs to be a list with a single element

    # we create a new list of dicts to hold the services
    Departures = [{}] * len(Services)

    for servicenum, eachService in enumerate(Services):
        thisDeparture = {}  # create empty dict to populate

        # next we move elements of dict eachService to dict thisDeparture one by one

        # get platform, if available
        if 'lt4:platform' in eachService:
            thisDeparture["platform"] = (eachService['lt4:platform'])

        # get scheduled departure time
        thisDeparture["aimed_departure_time"] = eachService["lt4:std"]

        # get estimated departure time
        thisDeparture["expected_departure_time"] = eachService["lt4:etd"]

        # get carriages, if available
        if 'lt4:length' in eachService:
            thisDeparture["carriages"] = eachService["lt4:length"]
        else:
            thisDeparture["carriages"] = 0

        # get operator, if available
        if 'lt4:operator' in eachService:
            thisDeparture["operator"] = eachService["lt4:operator"]

        # get name of destination
        if not isinstance(eachService['lt5:destination']['lt4:location'], list):    # the service only has one destination
            thisDeparture["destination_name"] = removeBrackets(eachService['lt5:destination']['lt4:location']['lt4:locationName'])
        else:  # the service splits and has multiple destinations
            DestinationList = [i['lt4:locationName'] for i in eachService['lt5:destination']['lt4:location']]
            thisDeparture["destination_name"] = " & ".join([removeBrackets(i) for i in DestinationList])

        # get via and add to destination name
        # if 'lt4:via' in eachService['lt5:destination']['lt4:location']:
        #    thisDeparture["destination_name"] += " " + eachService['lt5:destination']['lt4:location']['lt4:via']

            # get calling points
        if 'lt7:subsequentCallingPoints' in eachService:  # there are some calling points
            # check if it is a list of lists    (the train splits, so there are multiple lists of calling points)
            # or a dict                         (the train does not split. There is one list of calling points)
            if not isinstance(eachService['lt7:subsequentCallingPoints']['lt7:callingPointList'], dict):
                # there are multiple lists of calling points
                CallingPointList = eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']
                CallLists = []
                CallListJoined = []
                for sectionNum, eachSection in enumerate(CallingPointList):
                    if isinstance(eachSection['lt7:callingPoint'], dict):
                        # there is only one calling point in this list
                        CallLists.append([prepareLocationName(eachSection['lt7:callingPoint'], show_individual_departure_time)])
                        CallListJoined.append(CallLists[sectionNum])
                    else:  # there are several calling points in this list
                        CallLists.append([prepareLocationName(i, show_individual_departure_time) for i in eachSection['lt7:callingPoint']])

                        CallListJoined.append(joinwithCommas(CallLists[sectionNum]))
                        # CallListJoined.append(", ".join(CallLists[sectionNum]))
                thisDeparture["calling_at_list"] = joinWithSpaces(
                    " with a portion going to ".join(CallListJoined),
                    "  --  ",
                    prepareServiceMessage(thisDeparture["operator"]),
                    prepareCarriagesMessage(thisDeparture["carriages"])
                )

            else:  # there is one list of calling points
                if isinstance(eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']['lt7:callingPoint'], dict):
                    # there is only one calling point in the list
                    thisDeparture["calling_at_list"] = joinWithSpaces(
                        prepareLocationName(eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']['lt7:callingPoint'], show_individual_departure_time),
                        "only.",
                        "  --  ",
                        prepareServiceMessage(thisDeparture["operator"]),
                        prepareCarriagesMessage(thisDeparture["carriages"])
                    )
                else:  # there are several calling points in the list
                    CallList = [prepareLocationName(i, show_individual_departure_time) for i in eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']['lt7:callingPoint']]
                    thisDeparture["calling_at_list"] = joinWithSpaces(
                        joinwithCommas(CallList) + ".",
                        " --  ",
                        prepareServiceMessage(thisDeparture["operator"]),
                        prepareCarriagesMessage(thisDeparture["carriages"])
                    )
        else:  # there are no calling points, so just display the destination
            thisDeparture["calling_at_list"] = joinWithSpaces(
                thisDeparture["destination_name"],
                "only.",
                prepareServiceMessage(thisDeparture["operator"]),
                prepareCarriagesMessage(thisDeparture["carriages"])
            )
        # print("the " + thisDeparture["aimed_departure_time"] + " calls at " + thisDeparture["calling_at_list"])

        Departures[servicenum] = thisDeparture

    return Departures, departureStationName


def loadDeparturesForStation(journeyConfig):
    data = fetch_gtfs_data()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)  # Decode Protobuf

    now = whenever.Instant.now()

    if journeyConfig["departureStation"] == "":
        raise ValueError(
            "Please configure the departureStation environment variable")

    Departures, departureStationName = ProcessDepartures(journeyConfig, data)

    return Departures, departureStationName


# Description: Fetch and parse GTFS Realtime data from MTA API.

import csv

import requests
import whenever
from google.transit import gtfs_realtime_pb2

# Replace with your actual API key
API_KEY = "YOUR_API_KEY" # no longer required for MTA API
URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/mnr%2Fgtfs-mnr"

HUDSON_LINE_ROUTE_ID = "1"
BEACON_STOP = {"id": "46", "code": "0BC", "name": "Beacon"}
GRAND_CENTRAL_STOP = {"id": "1", "code": "0NY", "name": "Grand Central Terminal"}
PEEKSKILL_STOP = {"id": "39", "code": "0PE", "name": "Peekskill"}
COLDSPRING_STOP = {"id": "43", "code": "0CS", "name": "Cold Spring"}

with open("src/data/mnr/stops.txt", "r") as file:
    reader = csv.DictReader(file)
    stop_list = [row for row in reader]
    STOPS = {stop["stop_id"]: stop["stop_name"] for stop in stop_list}

def fetch_gtfs_data():
    """Fetch GTFS Realtime data from MTA API."""
    # headers = {"x-api-key": API_KEY}  # MTA API requires the x-api-key header # no longer required for MTA API
    headers = {}
    response = requests.get(URL, headers=headers)

    if response.status_code == 200:
        return response.content  # Return raw Protobuf data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def parse_gtfs_data(data):
    """Parse GTFS Realtime Protobuf data."""
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)  # Decode Protobuf

    now = whenever.Instant.now()

    print(f"Current Time: {now.timestamp()}")

    # print("GTFS Realtime Data:")
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            # Display Only Hudson Line Trips
            if entity.trip_update.trip.route_id == HUDSON_LINE_ROUTE_ID:
                trip_stops = {stu.stop_id: stu for stu in entity.trip_update.stop_time_update}
                if BEACON_STOP["id"] in trip_stops:
                    arrival_time = whenever.Instant.from_timestamp(trip_stops[BEACON_STOP["id"]].arrival.time)
                    if arrival_time.subtract(hours=1) < now and arrival_time.add(hours=1) > now:
                        trip_update = entity.trip_update
                        print(f"Trip ID: {trip_update.trip.trip_id}")
                        trip_direction = "Northbound" if trip_update.stop_time_update[0].stop_id == GRAND_CENTRAL_STOP["id"] else "Southbound"
                        print(f"  Direction: {trip_direction}")
                        for stop_time_update in trip_update.stop_time_update:
                            print(f"  Stop: {STOPS[stop_time_update.stop_id]}")
                            if stop_time_update.arrival.time:
                                arrival_time = whenever.ZonedDateTime.from_timestamp(stop_time_update.arrival.time, tz="America/New_York")
                                # print(f"    Arrival Time: {arrival_time.local().time().format_common_iso()}") # 24-hour format
                                print(f"    Arrival Time: {arrival_time.local().time().py_time().strftime('%-I:%M %p')}")

if __name__ == "__main__":
    raw_data = fetch_gtfs_data()
    if raw_data:
        parse_gtfs_data(raw_data)
