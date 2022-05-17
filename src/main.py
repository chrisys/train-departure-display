import os
import time

from datetime import datetime
from PIL import ImageFont

from trains import loadDeparturesForStation
from config import loadConfig
from open import isRun

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from luma.core.virtual import viewport, snapshot, hotspot
from luma.core.sprite_system import framerate_regulator

def makeFont(name, size):
    font_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'fonts',
            name
        )
    )
    return ImageFont.truetype(font_path, size)


def renderDestination(departure, font):
    departureTime = departure["aimed_departure_time"]
    destinationName = departure["destination_name"]

    def drawText(draw, width, height):
        train = f"{departureTime}  {destinationName}"
        draw.text((0, 0), text=train, font=font, fill="yellow")

    return drawText


def renderServiceStatus(departure):
    def drawText(draw, width, height):
        train = ""

        if departure["expected_departure_time"] == "On time":
            train = "On time"
        elif departure["expected_departure_time"] == "Cancelled":
            train = "Cancelled"
        elif departure["expected_departure_time"] == "Delayed":
            train = "Delayed"
        else:
            if isinstance(departure["expected_departure_time"], str):
                train = 'Exp '+departure["expected_departure_time"]

            if departure["aimed_departure_time"] == departure["expected_departure_time"]:
                train = "On time"

        w, h = draw.textsize(train, font)
        draw.text((width-w,0), text=train, font=font, fill="yellow")
    return drawText


def renderPlatform(departure):
    def drawText(draw, width, height):
        if "platform" in departure:
            if (departure["platform"].lower() == "bus"):
                draw.text((0, 0), text="BUS", font=font, fill="yellow")
            else:
                draw.text((0, 0), text="Plat "+departure["platform"], font=font, fill="yellow")
    return drawText


def renderCallingAt(draw, width, height):
    stations = "Calling at: "
    draw.text((0, 0), text=stations, font=font, fill="yellow")


def renderStations(stations):
    def drawText(draw, width, height):
        global stationRenderCount, pauseCount

        if(len(stations) == stationRenderCount - 5):
            stationRenderCount = 0

        draw.text(
            (0, 0), text=stations[stationRenderCount:], width=width, font=font, fill="yellow")

        if stationRenderCount == 0 and pauseCount < 8:
            pauseCount += 1
            stationRenderCount = 0
        else:
            pauseCount = 0
            stationRenderCount += 1

    return drawText

def renderTime(draw, width, height):
    rawTime = datetime.now().time()
    hour, minute, second = str(rawTime).split('.')[0].split(':')

    w1, h1 = draw.textsize("{}:{}".format(hour, minute), fontBoldLarge)
    w2, h2 = draw.textsize(":00", fontBoldTall)

    draw.text(((width - w1 - w2) / 2, 0), text="{}:{}".format(hour, minute),
              font=fontBoldLarge, fill="yellow")
    draw.text((((width - w1 - w2) / 2) + w1, 5), text=":{}".format(second),
              font=fontBoldTall, fill="yellow")


def renderWelcomeTo(xOffset):
    def drawText(draw, width, height):
        text = "Welcome to"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText

def renderPoweredBy(xOffset):
    def drawText(draw, width, height):
        text = "Powered by"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText

def renderNRE(xOffset):
    def drawText(draw, width, height):
        text = "National Rail Enquiries"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText

def renderName(xOffset):
    def drawText(draw, width, height):
        text = "UK Train Departure Display"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText

def renderDepartureStation(departureStation, xOffset):
    def draw(draw, width, height):
        text = departureStation
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return draw


def renderDots(draw, width, height):
    text = ".  .  ."
    draw.text((0, 0), text=text, font=fontBold, fill="yellow")


def loadData(apiConfig, journeyConfig, config):
    runHours = []
    if config['hoursPattern'].match(apiConfig['operatingHours']):
        runHours = [int(x) for x in apiConfig['operatingHours'].split('-')]

    if len(runHours) == 2 and isRun(runHours[0], runHours[1]) == False:
        return False, False, journeyConfig['outOfHoursName']

    if config['dualScreen'] == True:
        rows = "6"
    else:
        rows = "3"

    departures, stationName = loadDeparturesForStation(
        journeyConfig, apiConfig["apiKey"], rows)

    if (departures == None):
        return False, False, stationName

    firstDepartureDestinations = departures[0]["calling_at_list"]
    return departures, firstDepartureDestinations, stationName

def drawStartup(device, width, height):
    virtualViewport = viewport(device, width=width, height=height)

    with canvas(device) as draw:
        nameSize = draw.textsize("UK Train Departure Display", fontBold)
        poweredSize = draw.textsize("Powered by", fontBold)
        NRESize = draw.textsize("National Rail Enquiries", fontBold)

        rowOne = snapshot(width, 10, renderName((width - nameSize[0]) / 2), interval=10)
        rowThree = snapshot(width, 10, renderPoweredBy((width - poweredSize[0]) / 2), interval=10)
        rowFour = snapshot(width, 10, renderNRE((width - NRESize[0]) / 2), interval=10)

        if len(virtualViewport._hotspots) > 0:
            for hotspot, xy in virtualViewport._hotspots:
                virtualViewport.remove_hotspot(hotspot, xy)

        virtualViewport.add_hotspot(rowOne, (0, 0))
        virtualViewport.add_hotspot(rowThree, (0, 24))
        virtualViewport.add_hotspot(rowFour, (0, 36))

    return virtualViewport

def drawBlankSignage(device, width, height, departureStation):
    global stationRenderCount, pauseCount

    with canvas(device) as draw:
        welcomeSize = draw.textsize("Welcome to", fontBold)

    with canvas(device) as draw:
        stationSize = draw.textsize(departureStation, fontBold)

    device.clear()

    virtualViewport = viewport(device, width=width, height=height)

    rowOne = snapshot(width, 10, renderWelcomeTo(
        (width - welcomeSize[0]) / 2), interval=config["refreshTime"])
    rowTwo = snapshot(width, 10, renderDepartureStation(
        departureStation, (width - stationSize[0]) / 2), interval=config["refreshTime"])
    rowThree = snapshot(width, 10, renderDots, interval=config["refreshTime"])
    rowTime = hotspot(width, 14, renderTime)

    if len(virtualViewport._hotspots) > 0:
        for vhotspot, xy in virtualViewport._hotspots:
            virtualViewport.remove_hotspot(vhotspot, xy)

    virtualViewport.add_hotspot(rowOne, (0, 0))
    virtualViewport.add_hotspot(rowTwo, (0, 12))
    virtualViewport.add_hotspot(rowThree, (0, 24))
    virtualViewport.add_hotspot(rowTime, (0, 50))

    return virtualViewport

def platform_filter(departureData, platformNumber, nextStations, station):
    platformDepartures = []
    for sub in departureData:
        if platformNumber == "":
            platformDepartures.append(sub)
        elif sub.get('platform') is not None:
            if sub['platform'] == platformNumber:
                res = sub
                platformDepartures.append(res)

    if (len(platformDepartures) > 0):
        firstDepartureDestinations = platformDepartures[0]["calling_at_list"]
        platformData = platformDepartures, firstDepartureDestinations, station
    else:
        platformData = platformDepartures, "", station

    return platformData

def drawSignage(device, width, height, data):
    global stationRenderCount, pauseCount

    virtualViewport = viewport(device, width=width, height=height)

    status = "Exp 00:00"
    callingAt = "Calling at: "

    departures, firstDepartureDestinations, departureStation = data

    with canvas(device) as draw:
        w, h = draw.textsize(callingAt, font)

    callingWidth = w
    width = virtualViewport.width

    # First measure the text size
    with canvas(device) as draw:
        w, h = draw.textsize(status, font)
        pw, ph = draw.textsize("Plat 88", font)

    if(len(departures) == 0):
        noTrains = drawBlankSignage(device, width=width, height=height, departureStation=departureStation)
        return noTrains

    rowOneA = snapshot(
        width - w - pw - 5, 10, renderDestination(departures[0], fontBold), interval=config["refreshTime"])
    rowOneB = snapshot(w, 10, renderServiceStatus(
        departures[0]), interval=10)
    rowOneC = snapshot(pw, 10, renderPlatform(departures[0]), interval=config["refreshTime"])
    rowTwoA = snapshot(callingWidth, 10, renderCallingAt, interval=config["refreshTime"])
    rowTwoB = snapshot(width - callingWidth, 10,
                       renderStations(firstDepartureDestinations), interval=0.1)

    if(len(departures) > 1):
        rowThreeA = snapshot(width - w - pw, 10, renderDestination(
            departures[1], font), interval=config["refreshTime"])
        rowThreeB = snapshot(w, 10, renderServiceStatus(
            departures[1]), interval=config["refreshTime"])
        rowThreeC = snapshot(pw, 10, renderPlatform(departures[1]), interval=config["refreshTime"])

    if(len(departures) > 2):
        rowFourA = snapshot(width - w - pw, 10, renderDestination(
            departures[2], font), interval=10)
        rowFourB = snapshot(w, 10, renderServiceStatus(
            departures[2]), interval=10)
        rowFourC = snapshot(pw, 10, renderPlatform(departures[2]), interval=config["refreshTime"])

    rowTime = hotspot(width, 14, renderTime)

    if len(virtualViewport._hotspots) > 0:
        for vhotspot, xy in virtualViewport._hotspots:
            virtualViewport.remove_hotspot(vhotspot, xy)

    stationRenderCount = 0
    pauseCount = 0

    virtualViewport.add_hotspot(rowOneA, (0, 0))
    virtualViewport.add_hotspot(rowOneB, (width - w, 0))
    virtualViewport.add_hotspot(rowOneC, (width - w - pw, 0))
    virtualViewport.add_hotspot(rowTwoA, (0, 12))
    virtualViewport.add_hotspot(rowTwoB, (callingWidth, 12))

    if(len(departures) > 1):
        virtualViewport.add_hotspot(rowThreeA, (0, 24))
        virtualViewport.add_hotspot(rowThreeB, (width - w, 24))
        virtualViewport.add_hotspot(rowThreeC, (width - w - pw, 24))

    if(len(departures) > 2):
        virtualViewport.add_hotspot(rowFourA, (0, 36))
        virtualViewport.add_hotspot(rowFourB, (width - w, 36))
        virtualViewport.add_hotspot(rowFourC, (width - w - pw, 36))

    virtualViewport.add_hotspot(rowTime, (0, 50))

    return virtualViewport


try:
    version_file = open('VERSION', 'r')

    print('Starting Train Departure Display v' + version_file.read())
    config = loadConfig()

    serial = spi(port=0)
    device = ssd1322(serial, mode="1", rotate=config['screenRotation'])
    if config['dualScreen'] == True:
        serial1 = spi(port=1,gpio_DC=5, gpio_RST=6)
        device1 = ssd1322(serial1, mode="1", rotate=config['screenRotation'])
    font = makeFont("Dot Matrix Regular.ttf", 10)
    fontBold = makeFont("Dot Matrix Bold.ttf", 10)
    fontBoldTall = makeFont("Dot Matrix Bold Tall.ttf", 10)
    fontBoldLarge = makeFont("Dot Matrix Bold.ttf", 20)

    widgetWidth = 256
    widgetHeight = 64

    stationRenderCount = 0
    pauseCount = 0
    loop_count = 0

    regulator = framerate_regulator(20)

    # display NRE attribution while data loads
    virtual = drawStartup(device, width=widgetWidth, height=widgetHeight)
    virtual.refresh()
    if config['dualScreen'] == True:
        virtual = drawStartup(device1, width=widgetWidth, height=widgetHeight)
        virtual.refresh()
    time.sleep(5)

    timeAtStart = time.time()-config["refreshTime"]
    timeNow = time.time()
    
    blankHours = []
    if config['hoursPattern'].match(config['screenBlankHours']):
        blankHours = [int(x) for x in config['screenBlankHours'].split('-')]

    while True:
        with regulator:
            if len(blankHours) == 2 and isRun(blankHours[0], blankHours[1]) == True:
                device.clear()
                if config['dualScreen'] == True:
                    device1.clear()
                time.sleep(10)
            else:
                if(timeNow - timeAtStart >= config["refreshTime"]):

                    print('Effective FPS: ' + str(round(regulator.effective_FPS(),2)))
                    data = loadData(config["api"], config["journey"], config)
                    if data[0] == False:
                        virtual = drawBlankSignage(
                            device, width=widgetWidth, height=widgetHeight, departureStation=data[2])
                        if config['dualScreen'] == True:
                            virtual1 = drawBlankSignage(
                                device1, width=widgetWidth, height=widgetHeight, departureStation=data[2])
                    else:
                        departureData = data[0]
                        nextStations = data[1]
                        station = data[2]
                        screenData = platform_filter(departureData, config["journey"]["screen1Platform"], nextStations, station)
                        virtual = drawSignage(device, width=widgetWidth,height=widgetHeight, data=screenData)
                        
                        if config['dualScreen'] == True:
                            screen1Data = platform_filter(departureData, config["journey"]["screen2Platform"], nextStations, station)
                            virtual1 = drawSignage(device1, width=widgetWidth,height=widgetHeight, data=screen1Data)

                    timeAtStart = time.time()

                timeNow = time.time()
                virtual.refresh()
                if config['dualScreen'] == True:
                    virtual1.refresh()

except KeyboardInterrupt:
    pass
except ValueError as err:
    print(f"Error: {err}")
# except KeyError as err:
#     print(f"Error: Please ensure the {err} environment variable is set")
