import os
import sys
import time

from datetime import datetime
from PIL import ImageFont
from helpers import get_device
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

def renderDestination(draw, width, height):
    train = "08:54  London Waterloo"
    draw.text((0, 0), text=train, font=font, fill="yellow")

def renderServiceStatus(draw, width, height):
    train = "On time"

    draw.text((0, 0), text=train, font=font, fill="yellow")

def renderCallingAt(draw, width, height):
    stations = "Calling at:"
    draw.text((0, 0), text=stations, font=font, fill="yellow")


def renderStations(draw, width, height):
    global station_render_count

    stations = "Wimbledon, Earlsfield, Clapham Junction, Vauxhall and London Waterloo"
   
    if(len(stations) == station_render_count - 5):
      station_render_count = 0

    draw.text((0, 0), text=stations[station_render_count:], font=font, fill="yellow")
    station_render_count += 1

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

    draw.text(((256 - 84) / 2, 0), text="{}:{}".format(hour, minute), font=fontBoldLarge, fill="yellow")
    draw.text((((256 - 84) / 2) + w1, 3), text=":{}".format(second), font=fontBold, fill="yellow")

try:
  device = get_device()
  font = make_font("Dot Matrix Regular.ttf", 14)
  fontBold = make_font("Dot Matrix Bold.ttf", 14)
  fontBoldLarge = make_font("Dot Matrix Bold.ttf", 18)

  status = "On time"
  calling_at = "Calling at:"

  with canvas(device) as draw:
    w, h = draw.textsize(calling_at, font)

  calling_width = w

  # First measure the text size
  with canvas(device) as draw:
    w, h = draw.textsize(status, font)

  station_render_count = 0

  row_one_a = snapshot(256 - w, 16, renderDestination, interval=10)
  row_one_b = snapshot(w, 16, renderServiceStatus, interval=10)
  row_two_a = snapshot(calling_width, 16, renderCallingAt, interval=100)
  row_two_b = snapshot(256 - calling_width, 16, renderStations, interval=0.1)
  # row_three = snapshot(256, 16, renderSWR, interval=10)
  row_three = snapshot(256, 16, renderServiceDetails, interval=10)
  row_time = snapshot(256, 16, renderTime, interval=1)

  widget_width = 256
  widget_height = 64

  virtual = viewport(device, width=256, height=widget_height)
  virtual.add_hotspot(row_one_a, (0, 0))
  virtual.add_hotspot(row_one_b, (256 - w, 0))
  virtual.add_hotspot(row_two_a, (0, 16))
  virtual.add_hotspot(row_two_b, (calling_width, 16))
  virtual.add_hotspot(row_three, (0, 32))
  virtual.add_hotspot(row_time, (0, 48))


  while True:
    virtual.set_position((0, 0))
    
except KeyboardInterrupt:
    pass