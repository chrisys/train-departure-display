import os
import sys
import time
import json

from datetime import timedelta
from timeloop import Timeloop
from datetime import datetime
from PIL import ImageFont, Image
from helpers import get_device
from trains import loadDeparturesForStation, loadDestinationsForDeparture
from luma.core.render import canvas
from luma.core.virtual import viewport, snapshot


def loadConfig():
    with open('config.json', 'r') as jsonConfig:
        data = json.load(jsonConfig)
        return data


def makeFont(name, size):
    font_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'fonts',
            name
        )
    )
    return ImageFont.truetype(font_path, size)


def renderDestination(departure):
    departureTime = departure["aimed_departure_time"]
    destinationName = departure["destination_name"]

    def drawText(draw, width, height):
        train = f"{departureTime}  {destinationName}"
        draw.text((0, 0), text=train, font=font, fill="yellow")

    return drawText


def renderServiceStatus(departure):
    def drawText(draw, width, height):
        train = "On time" if departure["aimed_departure_time"] == departure[
            "expected_departure_time"] else departure["expected_departure_time"]

        draw.text((0, 0), text=train, font=font, fill="yellow")

    return drawText


def renderCallingAt(draw, width, height):
    stations = "Calling at:"
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


def renderServiceDetails(draw, width, height):
    details = "This train is formed of 10 coaches"
    draw.text((0, 0), text=details, font=font, fill="yellow")


def renderSWR(draw, width, height):
    swr = "SWR"
    draw.text((0, 0), text=swr, font=fontBold, fill="yellow")


def renderTime(draw, width, height):
    rawTime = datetime.now().time()
    hour, minute, second = str(rawTime).split('.')[0].split(':')

    w1, h1 = draw.textsize("{}:{}".format(hour, minute), fontBoldLarge)

    draw.text(((width - 84) / 2, 0), text="{}:{}".format(hour, minute),
              font=fontBoldLarge, fill="yellow")
    draw.text((((width - 84) / 2) + w1, 3), text=":{}".format(second),
              font=fontBold, fill="yellow")


def loadData(apiConfig, journeyConfig):
    departures = loadDeparturesForStation(
        journeyConfig, apiConfig["appId"], apiConfig["apiKey"])
    firstDepartureDestinations = loadDestinationsForDeparture(
        departures[0]["service_timetable"]["id"])

    return departures, firstDepartureDestinations


def drawSignage(device, width, height, data):
    global stationRenderCount, pauseCount

    device.clear()

    virtualViewport = viewport(device, width=width, height=height)

    status = "On time"
    callingAt = "Calling at:"

    departures, firstDepartureDestinations = data

    with canvas(device) as draw:
        w, h = draw.textsize(callingAt, font)

    callingWidth = w
    width = virtualViewport.width

    # First measure the text size
    with canvas(device) as draw:
        w, h = draw.textsize(status, font)

    rowOneA = snapshot(
        width - w, 16, renderDestination(departures[0]), interval=10)
    rowOneB = snapshot(w, 16, renderServiceStatus(
        departures[0]), interval=10)
    rowTwoA = snapshot(callingWidth, 16, renderCallingAt, interval=100)
    rowTwoB = snapshot(width - callingWidth, 16,
                       renderStations(", ".join(firstDepartureDestinations)), interval=0.1)
    rowThreeA = snapshot(width - w, 16, renderDestination(
        departures[1]), interval=10)
    rowThreeB = snapshot(w, 16, renderServiceStatus(
        departures[1]), interval=10)
    rowTime = snapshot(width, 14, renderTime, interval=1)

    if len(virtualViewport._hotspots) > 0:
        for hotspot, xy in virtualViewport._hotspots:
            virtualViewport.remove_hotspot(hotspot, xy)

    stationRenderCount = 0
    pauseCount = 0

    virtualViewport.add_hotspot(rowOneA, (0, 0))
    virtualViewport.add_hotspot(rowOneB, (width - w, 0))
    virtualViewport.add_hotspot(rowTwoA, (0, 16))
    virtualViewport.add_hotspot(rowTwoB, (callingWidth, 16))
    virtualViewport.add_hotspot(rowThreeA, (0, 32))
    virtualViewport.add_hotspot(rowThreeB, (width - w, 32))
    virtualViewport.add_hotspot(rowTime, (0, 50))

    return virtualViewport


try:
    config = loadConfig()

    device = get_device()
    font = makeFont("Dot Matrix Regular.ttf", 16)
    fontBold = makeFont("Dot Matrix Bold.ttf", 16)
    fontBoldLarge = makeFont("Dot Matrix Bold.ttf", 20)

    widgetWidth = 256
    widgetHeight = 64

    stationRenderCount = 0
    pauseCount = 0
    loop_count = 0

    data = loadData(config["transportApi"], config["journey"])
    virtual = drawSignage(device, width=widgetWidth,
                          height=widgetHeight, data=data)
    timeAtStart = time.time()
    timeNow = time.time()

    while True:
        if(timeNow - timeAtStart >= 60):
            data = loadData(config["transportApi"], config["journey"])
            virtual = drawSignage(device, width=widgetWidth,
                                  height=widgetHeight, data=data)
            timeAtStart = time.time()

        timeNow = time.time()
        virtual.refresh()


except KeyboardInterrupt:
    pass
except ValueError as err:
    print(f"Error: {err}")
except KeyError as err:
    print(f"Error: Please ensure the {err} environment variable is set")
