# UK Train Departure Display

A set of python scripts to display replica near real-time UK railway station departure data on SSD13xx style screens.
Uses the publicly available [Transport API](https://www.transportapi.com/).  

   * [Installation](#installation)
   * [Configuration](#configuration)
   * [Running](#running)

![](normal.gif)

## Installation

To run this code, you will need Python 3.6+

To install the latest version of Python (3.7 at time of writing) on Raspbian, go [here](https://gist.github.com/SeppPenner/6a5a30ebc8f79936fa136c524417761d).

You will likely need to set up an alias so that when you type Python you get the latest installed version, a handy guide on how to do this on Raspbin is [here](https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux).  If you used the above guide to install the latest Python your path to the executable will be /usr/local/bin/python3.x

>### Raspbian Lite
>If you're using Raspbian Lite, you'll also need to install:
>- `libopenjp2-7`
>with:
>```bash
>$ sudo apt-get install libopenjp2-7
>```

Clone this repo

Install dependencies

```bash
$ pip3 install -r requirements.txt
```
>If you installed Python using the above guide you will need to use pip3 instead of pip to install the requirements, if not or if your pip is aliased to python 3.6+ you can just use pip

## Configuration

Sign up for the [Transport API](https://www.transportapi.com/), and generate an app ID and API key (note the free tier has 1000 request a day).

Copy `config.sample.json` to `config.json` and complete.

```javascript
{
  "journey": {
    "departureStation": "",
    "destinationStation": null,
    "stationAbbr": {
      "International": "Intl."
    }
  },
  "refreshTime": 180,
  "transportApi": {
    "appId": "",
    "apiKey": "",
    "operatingHours": "0-23"
  }
}
```
### General Settings

`refreshTime` - how frequently it asks for new data from the transport api, there will be two api calls each time this time elapses, be aware the free tier has 1000 calls a day.

### Journey Settings

`departureStation` - the [short code](https://www.nationalrail.co.uk/stations_destinations/48541.aspx) for the starting station

`destinationStation` - the optional [short code](https://www.nationalrail.co.uk/stations_destinations/48541.aspx) for the destination station

`stationAbbr` - a list of words and their abbreviations that can be used to shorten station names, useful for small displays.

### Transport API Settings

`appId` - your transport api application ID

`apiKey` - your transport api key

`operating hours` - the range of hours you wish the display to actively request train times, be aware the free tier API has a limit of 1000 calls a day.


## Running

There is an example run.sh script in the root directory that will start the application and attempt to talk to a SSD1322 display via SPI.
You will need to adjust this to suit your own requirements

For example

Change the `--display` flag to alter the output mechanism (a list of options can be found in this README: https://github.com/rm-hull/luma.examples). Use `capture` to save to images, and `pygame` to run a visual emulator.

Pass `--interface spi` if you are using SPI to communicate with your screen. Otherwise, the default of `i2c` should suffice.

```bash
$ python ./src/main.py --display ssd1322 --width 256 --height 64 --interface spi
```

## BalenaCloud Installation

A Dockerfile template is included in order to run this project on the [balenaCloud](https://balena.io/cloud) platform.

To use this project, sign up, add an application and device as per the [getting started](https://www.balena.io/docs/learn/getting-started/raspberrypi3/python/) guide. Then use the [balena CLI](https://github.com/balena-io/balena-cli) to push the project to your Pi.

This allows you to easily deploy multiple devices and configure them from the dashboard with the following variables which will then automatically generate the `config.json` file:

| Key                              | Example Value
|----------------------------------|----------
|`TZ`  | `Europe/London` ([timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))
|`departureStation`  | `PAD` ([station code](https://www.nationalrail.co.uk/stations_destinations/48541.aspx))
|`refreshTime` | `120` (seconds between data refresh)
|`transportApi_apiKey` | `798c7ddfdeadbeef87987e9a8e79` (transport API key)
|`transportApi_appId` | `12345678` (transport API application ID)
|`transportApi_operatingHours` | `8-22` (hours during which the data will refresh at the interval above)


## Example Output

### Normal Operating Hours
![](normal.gif)
### Out Of Hours / No Trains
![](outofhours.gif)

## Video demo

Chris Hutchinson tweeted a video demo of the original software running on a real device: https://twitter.com/chrishutchinson/status/1136743837244768257 I will update this with a video of the modified version at some point in the future.

## Thanks

A big thanks to Chris Hutchinson who originally built this code! He can be found on GitHub at https://github.com/chrishutchinson/

The fonts used were painstakingly put together by `DanielHartUK` and can be found on GitHub at https://github.com/DanielHartUK/Dot-Matrix-Typeface - A huge thanks for making that resource available!
