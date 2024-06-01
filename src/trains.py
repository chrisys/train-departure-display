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
    return list(filter(None, items))  # Convert filter object to a list


def joinWith(items, joiner: str):
    filtered_list = removeEmptyStrings(items)
    return joiner.join(filtered_list)


def joinWithSpaces(*args):
    return joinWith(args, " ")


def prepareServiceMessage(operator):
    return joinWithSpaces(
        "A" if operator not in ["Elizabeth Line", "Avanti West Coast"] else "An",
        operator,
        "Service",
    )


def prepareLocationName(location, show_departure_time):
    location_name = removeBrackets(location["lt7:locationName"])

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
        STDHour = int(eachService["lt4:std"][0:2])
        STDMinute = int(eachService["lt4:std"][3:5])
        if STDHour < 2:
            STDHour += 24  # this prevents a 12am departure displaying before a 11pm departure
        STDinMinutes = STDHour * 60 + STDMinute  # this service is at this many minutes past midnight
        ServicesOUT.append(eachService)
        ServicesOUT[servicenum]["sortOrder"] = STDinMinutes
    ServicesOUT = sorted(ServicesOUT, key=lambda k: k["sortOrder"])
    return ServicesOUT


def ProcessDepartures(journeyConfig, APIOut):
    show_individual_departure_time = journeyConfig["individualStationDepartureTime"]
    APIElements = xmltodict.parse(APIOut)
    Services = []

    # Get departure station name
    departureStationName = APIElements["soap:Envelope"]["soap:Body"][
        "GetDepBoardWithDetailsResponse"
    ]["GetStationBoardResult"]["lt4:locationName"]

    # Handle different types of services (train-only, bus-only, mixed)
    if (
        "lt7:trainServices"
        in APIElements["soap:Envelope"]["soap:Body"]["GetDepBoardWithDetailsResponse"][
            "GetStationBoardResult"
        ]
    ):
        Services = APIElements["soap:Envelope"]["soap:Body"][
            "GetDepBoardWithDetailsResponse"
        ]["GetStationBoardResult"]["lt7:trainServices"]["lt7:service"]
        if isinstance(Services, dict):
            Services = [Services]
        if "lt7:busServices" in APIElements["soap:Envelope"]["soap:Body"][
            "GetDepBoardWithDetailsResponse"
        ]["GetStationBoardResult"]:
            BusServices = APIElements["soap:Envelope"]["soap:Body"][
                "GetDepBoardWithDetailsResponse"
            ]["GetStationBoardResult"]["lt7:busServices"]["lt7:service"]
            if isinstance(BusServices, dict):
                BusServices = [BusServices]
            Services = ArrivalOrder(Services + BusServices)
    elif (
        "lt7:busServices"
        in APIElements["soap:Envelope"]["soap:Body"]["GetDepBoardWithDetailsResponse"][
            "GetStationBoardResult"
        ]
    ):
        Services = APIElements["soap:Envelope"]["soap:Body"][
            "GetDepBoardWithDetailsResponse"
        ]["GetStationBoardResult"]["lt7:busServices"]["lt7:service"]
        if isinstance(Services, dict):
            Services = [Services]
    else:
        Services = None
        return None, departureStationName

    Departures = [{}] * len(Services)

    for servicenum, eachService in enumerate(Services):
        thisDeparture = {}
        
        # Extract platform, times, carriages, operator, destination_name
        if "lt4:platform" in eachService:
            thisDeparture["platform"] = eachService["lt4:platform"]
        thisDeparture["aimed_departure_time"] = eachService["lt4:std"]
        thisDeparture["expected_departure_time"] = eachService["lt4:etd"]
        if "lt4:length" in eachService:
            thisDeparture["carriages"] = eachService["lt4:length"]
        else:
            thisDeparture["carriages"] = 0
        if "lt4:operator" in eachService:
            thisDeparture["operator"] = eachService["lt4:operator"]

        if not isinstance(eachService["lt5:destination"]["lt4:location"], list):
            thisDeparture["destination_name"] = removeBrackets(
                eachService["lt5:destination"]["lt4:location"]["lt4:locationName"]
            )
        else:
            DestinationList = [
                i["lt4:locationName"] for i in eachService["lt5:destination"]["lt4:location"]
            ]
            thisDeparture["destination_name"] = " & ".join(
                [removeBrackets(i) for i in DestinationList]
            )

        # Check if the service calls at the specified "Via" station
        if "lt7:subsequentCallingPoints" in eachService:
            callingPoints = eachService["lt7:subsequentCallingPoints"]["lt7:callingPointList"]
            viaStationFound = False

            # Handle both single and multiple calling point lists
            if isinstance(callingPoints, dict):
                callingPoints = [callingPoints]

            for callingPointList in callingPoints:
                if isinstance(callingPointList["lt7:callingPoint"], list):
                    for point in callingPointList["lt7:callingPoint"]:
                        if (
                            removeBrackets(point["lt7:locationName"])
                            == journeyConfig["viaStation"]
                        ):
                            viaStationFound = True
                            break
                elif (
                    removeBrackets(callingPointList["lt7:callingPoint"]["lt7:locationName"])
                    == journeyConfig["viaStation"]
                ):
                    viaStationFound = True
                    break
        else:
            # No calling points, so it can't go via the specified station
            viaStationFound = False

        # Only include this service if it goes via the specified "Via" station or if no via station is specified
        if viaStationFound or not journeyConfig["viaStation"]:
            # Get calling points
            if "lt7:subsequentCallingPoints" in eachService:
                if not isinstance(
                    eachService["lt7:subsequentCallingPoints"]["lt7:callingPointList"],
                    dict,
                ):
                    CallingPointList = eachService["lt7:subsequentCallingPoints"]["lt7:callingPointList"]
                    CallLists = []
                    CallListJoined = []
                    for sectionNum, eachSection in enumerate(CallingPointList):
                        if isinstance(eachSection["lt7:callingPoint"], dict):
                            CallLists.append(
                                [
                                    prepareLocationName(
                                        eachSection["lt7:callingPoint"],
                                        show_individual_departure_time,
                                    )
                                ]
                            )
                            CallListJoined.append(CallLists[sectionNum])
                        else:
                            CallLists.append(
                                [
                                    prepareLocationName(i, show_individual_departure_time)
                                    for i in eachSection["lt7:callingPoint"]
                                ]
                            )

                            CallListJoined.append(joinwithCommas(CallLists[sectionNum]))
                    thisDeparture["calling_at_list"] = joinWithSpaces(
                        " with a portion going to ".join(CallListJoined),
                        " -- ",
