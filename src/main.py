import os
import time

import requests

from datetime import datetime
from PIL import ImageFont, Image, ImageDraw

from trains import loadDeparturesForStation
from config import loadConfig
from open import isRun

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.oled.device import ssd1322
from luma.core.virtual import viewport, snapshot
from luma.core.sprite_system import framerate_regulator

import socket, re, uuid

def makeFont(name, size):
    font_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'fonts',
            name
        )
    )
    return ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.BASIC)


def renderDestination(departure, font, pos):
    departureTime = departure["aimed_departure_time"]
    destinationName = departure["destination_name"]

    def drawText(draw, *_):
        if config["showDepartureNumbers"]:
            train = f"{pos}  {departureTime}  {destinationName}"
        else:
            train = f"{departureTime}  {destinationName}"
        _, _, bitmap = cachedBitmapText(train, font)
        draw.bitmap((0, 0), bitmap, fill="yellow")

    return drawText


def renderServiceStatus(departure):
    def drawText(draw, width, *_):
        train = ""

        if departure["expected_departure_time"] == "On time":
            train = "On time"
        elif departure["expected_departure_time"] == "Cancelled":
            train = "Cancelled"
        elif departure["expected_departure_time"] == "Delayed":
            train = "Delayed"
        else:
            if isinstance(departure["expected_departure_time"], str):
                train = 'Exp ' + departure["expected_departure_time"]

            if departure["aimed_departure_time"] == departure["expected_departure_time"]:
                train = "On time"

        w, _, bitmap = cachedBitmapText(train, font)
        draw.bitmap((width - w, 0), bitmap, fill="yellow")
    return drawText


def renderPlatform(departure):
    def drawText(draw, *_):
        if "platform" in departure:
            platform = "Plat " + departure["platform"]
            if departure["platform"].lower() == "bus":
                platform = "BUS"
            _, _, bitmap = cachedBitmapText(platform, font)
            draw.bitmap((0, 0), bitmap, fill="yellow")
    return drawText


def renderCallingAt(draw, *_):
    stations = "Calling at: "
    _, _, bitmap = cachedBitmapText(stations, font)
    draw.bitmap((0, 0), bitmap, fill="yellow")


bitmapRenderCache = {}


def cachedBitmapText(text, font):
    # cache the bitmap representation of the stations string
    nameTuple = font.getname()
    fontKey = ''
    for item in nameTuple:
        fontKey = fontKey + item
    key = text + fontKey
    if key in bitmapRenderCache:
        # found in cache; re-use it
        pre = bitmapRenderCache[key]
        bitmap = pre['bitmap']
        txt_width = pre['txt_width']
        txt_height = pre['txt_height']
    else:
        # not cached; create a new image containing the string as a monochrome bitmap
        _, _, txt_width, txt_height = font.getbbox(text)
        bitmap = Image.new('L', [txt_width, txt_height], color=0)
        pre_render_draw = ImageDraw.Draw(bitmap)
        pre_render_draw.text((0, 0), text=text, font=font, fill=255)
        # save to render cache
        bitmapRenderCache[key] = {'bitmap': bitmap, 'txt_width': txt_width, 'txt_height': txt_height}
    return txt_width, txt_height, bitmap


pixelsLeft = 1
pixelsUp = 0
hasElevated = 0
pauseCount = 0


def renderStations(stations):
    def drawText(draw, *_):
        global stationRenderCount, pauseCount, pixelsLeft, pixelsUp, hasElevated

        if len(stations) == stationRenderCount - 5:
            stationRenderCount = 0

        txt_width, txt_height, bitmap = cachedBitmapText(stations, font)

        if hasElevated:
            # slide the bitmap left until it's fully out of view
            draw.bitmap((pixelsLeft - 1, 0), bitmap, fill="yellow")
            if -pixelsLeft > txt_width and pauseCount < 8:
                pauseCount += 1
                pixelsLeft = 0
                hasElevated = 0
            else:
                pauseCount = 0
                pixelsLeft = pixelsLeft - 1
        else:
            # slide the bitmap up from the bottom of its viewport until it's fully in view
            draw.bitmap((0, txt_height - pixelsUp), bitmap, fill="yellow")
            if pixelsUp == txt_height:
                pauseCount += 1
                if pauseCount > 20:
                    hasElevated = 1
                    pixelsUp = 0
            else:
                pixelsUp = pixelsUp + 1

    return drawText


def renderTime(draw, width, *_):
    rawTime = datetime.now().time()
    hour, minute, second = str(rawTime).split('.')[0].split(':')

    w1, _, HMBitmap = cachedBitmapText("{}:{}".format(hour, minute), fontBoldLarge)
    w2, _, _ = cachedBitmapText(':00', fontBoldTall)
    _, _, SBitmap = cachedBitmapText(':{}'.format(second), fontBoldTall)

    draw.bitmap(((width - w1 - w2) / 2, 0), HMBitmap, fill="yellow")
    draw.bitmap((((width - w1 - w2) / 2) + w1, 5), SBitmap, fill="yellow")

def renderDebugScreen(lines):
    def drawDebug(draw, *_):
        # draw a box
        draw.rectangle((1, 1, 254, 45), outline="yellow", fill=None)

        # coords for each line of text
        coords = {
            '1A': (5, 5),
            '1B': (45, 5),
            '2A': (5, 18),
            '2B': (45, 18),
            '3A': (5, 31),
            '3B': (45, 31),
            '3C': (140, 31)
        }

        # loop through lines and check if cached
        for key, text in lines.items():
            w, _, bitmap = cachedBitmapText(text, font)
            draw.bitmap(coords[key], bitmap, fill="yellow")        

    return drawDebug

def renderWelcomeTo(xOffset):
    def drawText(draw, *_):
        text = "Welcome to"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText


def renderPoweredBy(xOffset):
    def drawText(draw, *_):
        text = "Powered by"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText


def renderNRE(xOffset):
    def drawText(draw, *_):
        text = "National Rail Enquiries"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText


def renderName(xOffset):
    def drawText(draw, *_):
        text = "UK Train Departure Display"
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return drawText


def renderDepartureStation(departureStation, xOffset):
    def draw(draw, *_):
        text = departureStation
        draw.text((int(xOffset), 0), text=text, font=fontBold, fill="yellow")

    return draw


def renderDots(draw, *_):
    text = ".  .  ."
    draw.text((0, 0), text=text, font=fontBold, fill="yellow")


def loadData(apiConfig, journeyConfig, config):
    runHours = []
    if config['hoursPattern'].match(apiConfig['operatingHours']):
        runHours = [int(x) for x in apiConfig['operatingHours'].split('-')]

    if len(runHours) == 2 and isRun(runHours[0], runHours[1]) is False:
        return False, False, journeyConfig['outOfHoursName']

    # set rows to 10 (max allowed) to get as many departure as poss
    # leaving as a variable so this can be updated if the API does
    rows = "10"

    try:
        departures, stationName = loadDeparturesForStation(
            journeyConfig, apiConfig["apiKey"], rows)

        if departures is None:
            return False, False, stationName

        firstDepartureDestinations = departures[0]["calling_at_list"]
        return departures, firstDepartureDestinations, stationName
    except requests.RequestException as err:
        print("Error: Failed to fetch data from OpenLDBWS")
        print(err.__context__)
        return False, False, journeyConfig['outOfHoursName']


def drawStartup(device, width, height):
    virtualViewport = viewport(device, width=width, height=height)

    with canvas(device):
        nameSize = int(fontBold.getlength("UK Train Departure Display"))
        poweredSize = int(fontBold.getlength("Powered by"))
        NRESize = int(fontBold.getlength("National Rail Enquiries"))

        rowOne = snapshot(width, 10, renderName((width - nameSize) / 2), interval=10)
        rowThree = snapshot(width, 10, renderPoweredBy((width - poweredSize) / 2), interval=10)
        rowFour = snapshot(width, 10, renderNRE((width - NRESize) / 2), interval=10)

        if len(virtualViewport._hotspots) > 0:
            for hotspot, xy in virtualViewport._hotspots:
                virtualViewport.remove_hotspot(hotspot, xy)

        virtualViewport.add_hotspot(rowOne, (0, 0))
        virtualViewport.add_hotspot(rowThree, (0, 24))
        virtualViewport.add_hotspot(rowFour, (0, 36))

    return virtualViewport

def drawDebugScreen(device, width, height, screen="1", showTime=False):
    virtualViewport = viewport(device, width=width, height=height)

    versionNumber = getVersionNumber().strip()
    
    ipAddress = getIp()

    macAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode())).upper()

    debugLines = {}

    # ok let's build the strings, there's a bit of optional data here so let's do it the old fashioned way with appends

    debugLines["1A"] = "Display"

    debugLines["1B"] = f"= {config['journey']['departureStation']}"

    # has a destination been set? add it in!
    if(config["journey"]["destinationStation"]):
        debugLines["1B"] += f"->{config['journey']['destinationStation']}"

    # what about a plaform?
    if(config["journey"]["screen"+screen+"Platform"]):
        debugLines["1B"] += f" (Plat{config['journey']['screen'+screen+'Platform']}) "
    else:
        debugLines["1B"] += " (PlatAll) "

    # refresh time
    debugLines["1B"] += f"{config['refreshTime']}s "
    
    # this wasn't set on my default so will wrap it in if, just in case
    if(config['api']['operatingHours']):
        debugLines["1B"] += f"{config['api']['operatingHours']}h"
    
    debugLines["2A"] = "Script"
    debugLines["2B"] = f"= T_D_D:  {versionNumber}"

    debugLines["3A"] = "Address"
    debugLines["3B"] = f"= {macAddress}"
    debugLines["3C"] = f"IP={ipAddress}"

    theBox = snapshot(width, 64, renderDebugScreen(debugLines), interval=config["refreshTime"])
    virtualViewport.add_hotspot(theBox, (0, 0))

    if(showTime):
        rowTime = snapshot(width, 14, renderTime, interval=0.1)
        virtualViewport.add_hotspot(rowTime, (0, 50))

    return virtualViewport




def drawBlankSignage(device, width, height, departureStation):
    global stationRenderCount, pauseCount

    welcomeSize = int(fontBold.getlength("Welcome to"))
    stationSize = int(fontBold.getlength(departureStation))

    device.clear()

    virtualViewport = viewport(device, width=width, height=height)

    rowOne = snapshot(width, 10, renderWelcomeTo(
        (width - welcomeSize) / 2), interval=config["refreshTime"])
    rowTwo = snapshot(width, 10, renderDepartureStation(
        departureStation, (width - stationSize) / 2), interval=config["refreshTime"])
    rowThree = snapshot(width, 10, renderDots, interval=config["refreshTime"])
    # this will skip a second sometimes if set to 1, but a hotspot burns CPU
    # so set to snapshot of 0.1; you won't notice
    rowTime = snapshot(width, 14, renderTime, interval=0.1)

    if len(virtualViewport._hotspots) > 0:
        for vhotspot, xy in virtualViewport._hotspots:
            virtualViewport.remove_hotspot(vhotspot, xy)

    virtualViewport.add_hotspot(rowOne, (0, 0))
    virtualViewport.add_hotspot(rowTwo, (0, 12))
    virtualViewport.add_hotspot(rowThree, (0, 24))
    virtualViewport.add_hotspot(rowTime, (0, 50))

    return virtualViewport


def platform_filter(departureData, platformNumber, station):
    platformDepartures = []
    for sub in departureData:
        if platformNumber == "":
            platformDepartures.append(sub)
        elif sub.get('platform') is not None:
            if sub['platform'] == platformNumber:
                res = sub
                platformDepartures.append(res)

    if len(platformDepartures) > 0:
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

    w = int(font.getlength(callingAt))

    callingWidth = w
    width = virtualViewport.width

    # First measure the text size
    w = int(font.getlength(status))
    pw = int(font.getlength("Plat 88"))

    if len(departures) == 0:
        noTrains = drawBlankSignage(device, width=width, height=height, departureStation=departureStation)
        return noTrains

    firstFont = font
    if config['firstDepartureBold']:
        firstFont = fontBold

    rowOneA = snapshot(
        width - w - pw - 5, 10, renderDestination(departures[0], firstFont, '1st'), interval=config["refreshTime"])
    rowOneB = snapshot(w, 10, renderServiceStatus(
        departures[0]), interval=10)
    rowOneC = snapshot(pw, 10, renderPlatform(departures[0]), interval=config["refreshTime"])
    rowTwoA = snapshot(callingWidth, 10, renderCallingAt, interval=config["refreshTime"])
    rowTwoB = snapshot(width - callingWidth, 10,
                       renderStations(firstDepartureDestinations), interval=0.02)

    if len(departures) > 1:
        rowThreeA = snapshot(width - w - pw, 10, renderDestination(
            departures[1], font, '2nd'), interval=config["refreshTime"])
        rowThreeB = snapshot(w, 10, renderServiceStatus(
            departures[1]), interval=config["refreshTime"])
        rowThreeC = snapshot(pw, 10, renderPlatform(departures[1]), interval=config["refreshTime"])

    if len(departures) > 2:
        rowFourA = snapshot(width - w - pw, 10, renderDestination(
            departures[2], font, '3rd'), interval=10)
        rowFourB = snapshot(w, 10, renderServiceStatus(
            departures[2]), interval=10)
        rowFourC = snapshot(pw, 10, renderPlatform(departures[2]), interval=config["refreshTime"])

    rowTime = snapshot(width, 14, renderTime, interval=0.1)

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

    if len(departures) > 1:
        virtualViewport.add_hotspot(rowThreeA, (0, 24))
        virtualViewport.add_hotspot(rowThreeB, (width - w, 24))
        virtualViewport.add_hotspot(rowThreeC, (width - w - pw, 24))

    if len(departures) > 2:
        virtualViewport.add_hotspot(rowFourA, (0, 36))
        virtualViewport.add_hotspot(rowFourB, (width - w, 36))
        virtualViewport.add_hotspot(rowFourC, (width - w - pw, 36))

    virtualViewport.add_hotspot(rowTime, (0, 50))

    return virtualViewport

def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def getVersionNumber():
    version_file = open('VERSION', 'r')
    return version_file.read()

try:
    print('Starting Train Departure Display v' + getVersionNumber())
    config = loadConfig()
    if config['headless']:
        print('Headless mode, running main loop without serial comms')
        serial = noop()
    else:
        serial = spi(port=0)
    device = ssd1322(serial, mode="1", rotate=config['screenRotation'])

    if config['dualScreen']:
        serial1 = spi(port=1, gpio_DC=5, gpio_RST=6)
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

    regulator = framerate_regulator(config['targetFPS'])

    if (config['debug'] > 1):
        # render screen and sleep for specified seconds
        virtual = drawDebugScreen(device, width=widgetWidth, height=widgetHeight)
        virtual.refresh()
        if config['dualScreen']:
            virtual = drawDebugScreen(device, width=widgetWidth, height=widgetHeight, screen="2")
            virtual.refresh()
        time.sleep(config['debug'])
    else:
        # display NRE attribution while data loads
        virtual = drawStartup(device, width=widgetWidth, height=widgetHeight)
        virtual.refresh()
        if config['dualScreen']:
            virtual = drawStartup(device1, width=widgetWidth, height=widgetHeight)
            virtual.refresh()
        if config['headless'] is not True:
            time.sleep(5)

    timeAtStart = time.time() - config["refreshTime"]
    timeNow = time.time()
    timeFPS = time.time()

    blankHours = []
    if config['hoursPattern'].match(config['screenBlankHours']):
        blankHours = [int(x) for x in config['screenBlankHours'].split('-')]

    while True:
        with regulator:
            if len(blankHours) == 2 and isRun(blankHours[0], blankHours[1]):
                device.clear()
                if config['dualScreen']:
                    device1.clear()
                time.sleep(10)
            else:
                if timeNow - timeFPS >= config['fpsTime']:
                    timeFPS = time.time()
                    print('Effective FPS: ' + str(round(regulator.effective_FPS(), 2)))
                if timeNow - timeAtStart >= config["refreshTime"]:
                    # check if debug mode is enabled 
                    if config["debug"] == True:
                        print(config["debug"])
                        virtual = drawDebugScreen(device, width=widgetWidth, height=widgetHeight, showTime=True)
                        if config['dualScreen']:
                            virtual1 = drawDebugScreen(device1, width=widgetWidth, height=widgetHeight, showTime=True, screen="2")
                    else:
                        data = loadData(config["api"], config["journey"], config)
                        if data[0] is False:
                            virtual = drawBlankSignage(
                                device, width=widgetWidth, height=widgetHeight, departureStation=data[2])
                            if config['dualScreen']:
                                virtual1 = drawBlankSignage(
                                    device1, width=widgetWidth, height=widgetHeight, departureStation=data[2])
                        else:
                            departureData = data[0]
                            nextStations = data[1]
                            station = data[2]
                            screenData = platform_filter(departureData, config["journey"]["screen1Platform"], station)
                            virtual = drawSignage(device, width=widgetWidth, height=widgetHeight, data=screenData)
                            # virtual = drawDebugScreen(device, width=widgetWidth, height=widgetHeight, showTime=True)

                            if config['dualScreen']:
                                screen1Data = platform_filter(departureData, config["journey"]["screen2Platform"], station)
                                virtual1 = drawSignage(device1, width=widgetWidth, height=widgetHeight, data=screen1Data)

                    timeAtStart = time.time()

                timeNow = time.time()
                virtual.refresh()
                if config['dualScreen']:
                    virtual1.refresh()

except KeyboardInterrupt:
    pass
except ValueError as err:
    print(f"Error: {err}")
# except KeyError as err:
#     print(f"Error: Please ensure the {err} environment variable is set")
