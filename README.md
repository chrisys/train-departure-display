# UK Train Departure Display 

A set of python scripts to display replica near real-time UK railway station departure data on SSD13xx style screens that uses the publicly available [Transport API](https://www.transportapi.com/).  

   * [Installation](#installation)
   * [Configuration](#configuration)

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
