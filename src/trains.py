import requests
import re
import xmltodict

def removeBrackets(originalName):
    return re.split(r" \(",originalName)[0]

def joinwithCommas(listIN):
    return ", ".join(listIN)[::-1].replace(",", "dna ", 1)[::-1]


def ArrivalOrder(ServicesIN):
    ServicesOUT = []
    for servicenum, eachService in enumerate(ServicesIN):
        STDHour = int(eachService['lt4:std'][0:2])
        STDMinute = int(eachService['lt4:std'][3:5])
        if (STDHour < 2):
            STDHour += 24 # this prevents a 12am departure displaying before a 11pm departure
        STDinMinutes = STDHour*60 + STDMinute # this service is at this many minutes past midnight
        ServicesOUT.append(eachService)
        ServicesOUT[servicenum]['sortOrder'] = STDinMinutes
    ServicesOUT = sorted(ServicesOUT, key=lambda k: k['sortOrder'])
    return ServicesOUT

def ProcessDepartures(APIOut):
    APIElements = xmltodict.parse(APIOut)
    Services = []

    # get departure station name
    departureStationName = APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']['lt4:locationName']

    # if there are only train services from this station
    if 'lt7:trainServices' in APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']:
        Services = APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']['lt7:trainServices']['lt7:service']
        if isinstance(Services, dict):  # if there's only one service, it comes out as a dict
            Services = [Services]       # but it needs to be a list with a single element

        # if there are train and bus services from this station
        if 'lt7:busServices' in APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']:
            BusServices = APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']['lt7:busServices']['lt7:service']
            if isinstance(BusServices, dict):
                BusServices = [BusServices]
            Services = ArrivalOrder(Services + BusServices) # sort the bus and train services into one list in order of scheduled arrival time

    # if there are only bus services from this station
    elif 'lt7:busServices' in APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']:
        Services = APIElements['soap:Envelope']['soap:Body']['GetDepBoardWithDetailsResponse']['GetStationBoardResult']['lt7:busServices']['lt7:service']
        if isinstance(Services, dict):
            Services = [Services]

    # if there are no trains or buses
    else:
        Services = None
        return None, departureStationName


    # we create a new list of dicts to hold the services
    Departures = [{}] * len(Services)


    for servicenum, eachService in enumerate(Services):
        thisDeparture = {} # create empty dict to populate

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
            thisDeparture["carriages"] = " formed of "+eachService["lt4:length"]+" coaches."
        else:
            thisDeparture["carriages"] = ""

        # get operator, if available
        if 'lt4:operator' in eachService:
            thisDeparture["operator"] = eachService["lt4:operator"]

        # get name of destination
        if not isinstance(eachService['lt5:destination']['lt4:location'],list):    # the service only has one destination
            thisDeparture["destination_name"] = removeBrackets(eachService['lt5:destination']['lt4:location']['lt4:locationName'])
        else: # the service splits and has multiple destinations
            DestinationList = [i['lt4:locationName'] for i in eachService['lt5:destination']['lt4:location']]
            thisDeparture["destination_name"] = " & ".join([removeBrackets(i) for i in DestinationList])

        # get via and add to destination name
        #if 'lt4:via' in eachService['lt5:destination']['lt4:location']:
        #    thisDeparture["destination_name"] += " " + eachService['lt5:destination']['lt4:location']['lt4:via']

            # get calling points
        if 'lt7:subsequentCallingPoints' in eachService: # there are some calling points
            # check if it is a list of lists    (the train splits, so there are multiple lists of calling points)
            # or a dict                         (the train does not split. There is one list of calling points)
            if not isinstance(eachService['lt7:subsequentCallingPoints']['lt7:callingPointList'],dict):
                # there are multiple lists of calling points
                CallingPointList = eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']
                CallLists = []
                CallListJoined = []
                for sectionNum, eachSection in enumerate(CallingPointList):
                    if isinstance(eachSection['lt7:callingPoint'], dict):
                        # there is only one calling point in this list
                        CallLists.append([eachSection['lt7:callingPoint']['lt7:locationName']])
                        CallListJoined.append(CallLists[sectionNum])
                    else: # there are several calling points in this list
                        CallLists.append([removeBrackets(i['lt7:locationName']) for i in eachSection['lt7:callingPoint']])

                        CallListJoined.append(joinwithCommas(CallLists[sectionNum]))
                        # CallListJoined.append(", ".join(CallLists[sectionNum]))
                thisDeparture["calling_at_list"] = " with a portion going to ".join(CallListJoined) + ".   --   A "+thisDeparture["operator"]+" Service"+thisDeparture["carriages"]

            else: # there is one list of calling points
                if isinstance(eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']['lt7:callingPoint'],dict):
                    # there is only one calling point in the list
                    thisDeparture["calling_at_list"] = eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']['lt7:callingPoint']['lt7:locationName'] + " only.   --   A "+thisDeparture["operator"]+" Service"+thisDeparture["carriages"]
                else: # there are several calling points in the list
                    CallList = [removeBrackets(i['lt7:locationName']) for i in eachService['lt7:subsequentCallingPoints']['lt7:callingPointList']['lt7:callingPoint']]
                    thisDeparture["calling_at_list"] = joinwithCommas(CallList) + ".   --   A "+thisDeparture["operator"]+" Service"+thisDeparture["carriages"]

                    # thisDeparture["calling_at_list"] = ", ".join(CallList)
        else: # there are no calling points, so just display the destination
            thisDeparture["calling_at_list"] = thisDeparture["destination_name"] + " only.   --   A "+thisDeparture["operator"]+" Service"+thisDeparture["carriages"]

        #print("the " + thisDeparture["aimed_departure_time"] + " calls at " + thisDeparture["calling_at_list"])

        Departures[servicenum] = thisDeparture

    return Departures, departureStationName

def loadDeparturesForStation(journeyConfig, apiKey, rows):
    if journeyConfig["departureStation"] == "":
        raise ValueError(
            "Please configure the departureStation environment variable")

    if apiKey == None:
        raise ValueError(
            "Please configure the apiKey environment variable")

    APIRequest = """
        <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ldb="http://thalesgroup.com/RTTI/2017-10-01/ldb/" xmlns:typ4="http://thalesgroup.com/RTTI/2013-11-28/Token/types">
        <x:Header>
            <typ4:AccessToken><typ4:TokenValue>""" + apiKey + """</typ4:TokenValue></typ4:AccessToken>
        </x:Header>
        <x:Body>
            <ldb:GetDepBoardWithDetailsRequest>
                <ldb:numRows>""" + rows + """</ldb:numRows>
                <ldb:crs>""" + journeyConfig["departureStation"] + """</ldb:crs>
                <ldb:timeOffset>""" + journeyConfig["timeOffset"] + """</ldb:timeOffset>
                <ldb:filterCrs>""" + journeyConfig["destinationStation"] + """</ldb:filterCrs>
                <ldb:filterType>to</ldb:filterType>
                <ldb:timeWindow>120</ldb:timeWindow>
            </ldb:GetDepBoardWithDetailsRequest>
        </x:Body>
    </x:Envelope>"""


    headers = {'Content-Type': 'text/xml'}
    apiURL = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb11.asmx"

    APIOut = requests.post(apiURL, data=APIRequest, headers=headers).text

    Departures, departureStationName = ProcessDepartures(APIOut)

    return Departures, departureStationName
