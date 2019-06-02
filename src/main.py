import os
import sys
import time
import threading

from datetime import timedelta
from timeloop import Timeloop
from datetime import datetime
from PIL import ImageFont, Image
from helpers import get_device
from trains import loadDeparturesForStation, loadDestinationsForDeparture
from luma.core.render import canvas
from luma.core.virtual import viewport, snapshot


def make_font(name, size):
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
        global station_render_count, pause_count

        if(len(stations) == station_render_count - 5):
            station_render_count = 0

        draw.text(
            (0, 0), text=stations[station_render_count:], width=width, font=font, fill="yellow")

        if station_render_count == 0 and pause_count < 8:
            pause_count += 1
            station_render_count = 0
        else:
            pause_count = 0
            station_render_count += 1

    return drawText


def renderServiceDetails(draw, width, height):
    details = "This train is formed of 10 coaches"
    draw.text((0, 0), text=details, font=font, fill="yellow")


def renderSWR(draw, width, height):
    swr = "SWR"
    draw.text((0, 0), text=swr, font=fontBold, fill="yellow")


def renderTime(draw, width, height):
    raw_time = datetime.now().time()
    hour, minute, second = str(raw_time).split('.')[0].split(':')

    w1, h1 = draw.textsize("{}:{}".format(hour, minute), fontBoldLarge)

    draw.text(((width - 84) / 2, 0), text="{}:{}".format(hour, minute),
              font=fontBoldLarge, fill="yellow")
    draw.text((((width - 84) / 2) + w1, 3), text=":{}".format(second),
              font=fontBold, fill="yellow")


def loadData():
    departures = loadDeparturesForStation(
        DEPARTURE_STATION_CODE, TRANSPORT_APP_ID, TRANSPORT_API_KEY)
    firstDepartureDestinations = loadDestinationsForDeparture(
        departures[0]["service_timetable"]["id"])

    return departures, firstDepartureDestinations


def startRefreshTimer(device, width, height):
    tl = Timeloop()

    @tl.job(interval=timedelta(seconds=0.2))
    def screenRefresh():
        global virtual
        if virtual is not None:
            virtual.refresh()

    @tl.job(interval=timedelta(seconds=5))
    def reloadDataAndRedraw():
        global virtual
        data = loadData()
        virtual = drawSignage(device, width, height, data)
        virtual.refresh()

    tl.start(block=True)


def drawSignage(device, width, height, data):
    global station_render_count, pause_count

    device.clear()

    virtualViewport = viewport(device, width=width, height=height)

    status = "On time"
    calling_at = "Calling at:"

    departures, firstDepartureDestinations = data

    with canvas(device) as draw:
        w, h = draw.textsize(calling_at, font)

    calling_width = w
    width = virtualViewport.width

    # First measure the text size
    with canvas(device) as draw:
        w, h = draw.textsize(status, font)

    row_one_a = snapshot(
        width - w, 16, renderDestination(departures[0]), interval=10)
    row_one_b = snapshot(w, 16, renderServiceStatus(
        departures[0]), interval=10)
    row_two_a = snapshot(calling_width, 16, renderCallingAt, interval=100)
    row_two_b = snapshot(width - calling_width, 16,
                         renderStations(", ".join(firstDepartureDestinations)), interval=0.2)
    row_three_a = snapshot(width - w, 16, renderDestination(
        departures[1]), interval=10)
    row_three_b = snapshot(w, 16, renderServiceStatus(
        departures[1]), interval=10)
    row_time = snapshot(width, 16, renderTime, interval=1)

    if len(virtualViewport._hotspots) > 0:
        for hotspot, xy in virtualViewport._hotspots:
            virtualViewport.remove_hotspot(hotspot, xy)

    station_render_count = 0
    pause_count = 0

    virtualViewport.add_hotspot(row_one_a, (0, 0))
    virtualViewport.add_hotspot(row_one_b, (width - w, 0))
    virtualViewport.add_hotspot(row_two_a, (0, 16))
    virtualViewport.add_hotspot(row_two_b, (calling_width, 16))
    virtualViewport.add_hotspot(row_three_a, (0, 32))
    virtualViewport.add_hotspot(row_three_b, (width - w, 32))
    virtualViewport.add_hotspot(row_time, (0, 48))

    return virtualViewport


try:
    DEPARTURE_STATION_CODE = os.environ["DEPARTURE_STATION_CODE"]
    TRANSPORT_APP_ID = os.environ["TRANSPORT_APP_ID"]
    TRANSPORT_API_KEY = os.environ["TRANSPORT_API_KEY"]

    device = get_device()
    font = make_font("Dot Matrix Regular.ttf", 14)
    fontBold = make_font("Dot Matrix Bold.ttf", 14)
    fontBoldLarge = make_font("Dot Matrix Bold.ttf", 18)

    # Global container for the virtual viewport
    virtual = None

    station_render_count = 0
    pause_count = 0

    widget_width = 256
    widget_height = 64

    startRefreshTimer(device, width=widget_width, height=widget_height)


except KeyboardInterrupt:
    pass
except ValueError as err:
    print(f"Error: {err}")
except KeyError as err:
    print(f"Error: Please ensure the {err} environment variable is set")
