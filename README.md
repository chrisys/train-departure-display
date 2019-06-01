# UK train departure screen

> Python script to display replica real-time (coming soon) UK railway station departure screens for SSD13xx devices

## Sample output

![Example output of the script](capture.png)

## Usage

1. Clone this repo

2. Install dependcies

```bash
$ pip install -r requirements.txt
```

3. Sign up for the [Transport API](https://www.transportapi.com/), and generate an app ID and API key

4. Run the script, providing your app ID and API key from step 3 as environment variables, along with a departure station code ([list](https://www.nationalrail.co.uk/stations_destinations/48541.aspx)):

```bash
$ DEPARTURE_STATION_CODE= TRANSPORT_APP_ID= TRANSPORT_API_KEY= python ./src/main.py --display pygame --width 256 --height 64

```

Change the `--display` flag to alter the output mechanism (a list of options can be found in this README: https://github.com/rm-hull/luma.examples). Use `capture` to save to images, and `pygame` to run a visual emulator.

## Thanks

The fonts used were painstakingly put together by `DanielHartUK` and can be found on GitHub at https://github.com/DanielHartUK/Dot-Matrix-Typeface - A huge thanks for making that resource available!
