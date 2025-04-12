# Description: Fetch and parse GTFS Realtime data from MTA API.

import csv

import requests
import whenever
from google.transit import gtfs_realtime_pb2

# Replace with your actual API key
API_KEY = "YOUR_API_KEY" # no longer required for MTA API
URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/mnr%2Fgtfs-mnr"

HUDSON_LINE_ROUTE_ID = "1"
BEACON_STOP = {"id": "46", "code": "0BC", "name": "Beacon"}
GRAND_CENTRAL_STOP = {"id": "1", "code": "0NY", "name": "Grand Central Terminal"}
PEEKSKILL_STOP = {"id": "39", "code": "0PE", "name": "Peekskill"}
COLDSPRING_STOP = {"id": "43", "code": "0CS", "name": "Cold Spring"}

with open("src/data/mnr/stops.txt", "r") as file:
    reader = csv.DictReader(file)
    stop_list = [row for row in reader]
    STOPS = {stop["stop_id"]: stop["stop_name"] for stop in stop_list}

def fetch_gtfs_data():
    """Fetch GTFS Realtime data from MTA API."""
    # headers = {"x-api-key": API_KEY}  # MTA API requires the x-api-key header # no longer required for MTA API
    headers = {}
    response = requests.get(URL, headers=headers)

    if response.status_code == 200:
        return response.content  # Return raw Protobuf data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def parse_gtfs_data(data):
    """Parse GTFS Realtime Protobuf data."""
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)  # Decode Protobuf

    now = whenever.Instant.now()

    print(f"Current Time: {now.timestamp()}")

    # print("GTFS Realtime Data:")
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            # Display Only Hudson Line Trips
            if entity.trip_update.trip.route_id == HUDSON_LINE_ROUTE_ID:
                trip_stops = {stu.stop_id: stu for stu in entity.trip_update.stop_time_update}
                if BEACON_STOP["id"] in trip_stops:
                    arrival_time = whenever.Instant.from_timestamp(trip_stops[BEACON_STOP["id"]].arrival.time)
                    if arrival_time.subtract(hours=1) < now and arrival_time.add(hours=1) > now:
                        trip_update = entity.trip_update
                        print(f"Trip ID: {trip_update.trip.trip_id}")
                        trip_direction = "Northbound" if trip_update.stop_time_update[0].stop_id == GRAND_CENTRAL_STOP["id"] else "Southbound"
                        print(f"  Direction: {trip_direction}")
                        for stop_time_update in trip_update.stop_time_update:
                            print(f"  Stop: {STOPS[stop_time_update.stop_id]}")
                            if stop_time_update.arrival.time:
                                arrival_time = whenever.ZonedDateTime.from_timestamp(stop_time_update.arrival.time, tz="America/New_York")
                                # print(f"    Arrival Time: {arrival_time.local().time().format_common_iso()}") # 24-hour format
                                print(f"    Arrival Time: {arrival_time.local().time().py_time().strftime('%-I:%M %p')}")

if __name__ == "__main__":
    raw_data = fetch_gtfs_data()
    if raw_data:
        parse_gtfs_data(raw_data)
