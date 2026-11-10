import csv
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

# Date range to download (inclusive)
START = date(2026, 9, 1)
END = date(2026, 9, 30)
CARPARK_EVERY_HOURS = 1

OUTPUT = Path("CA1_Datasets")
OUTPUT.mkdir(exist_ok=True)

RAINFALL_URL = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"
CARPARK_URL = "https://api.data.gov.sg/v1/transport/carpark-availability"


def get_json(url, params):
    # Wait and retry when the rate limit is hit
    for _ in range(10):
        response = requests.get(url, params=params, timeout=60)
        if response.status_code != 429:
            response.raise_for_status()
            return response.json()
        time.sleep(11)
    raise RuntimeError(f"Still rate limited: {url} {params}")


def days():
    day = START
    while day <= END:
        yield day
        day += timedelta(days=1)


def download_rainfall():
    path = OUTPUT / f"rainfall_{START:%Y%m%d}_{END:%Y%m%d}.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "station_id", "station_name",
                         "latitude", "longitude", "rainfall_mm"])
        for day in days():
            params = {"date": day.isoformat()}
            while True:
                data = get_json(RAINFALL_URL, params)["data"]
                stations = {s["id"]: s for s in data["stations"]}
                for reading in data["readings"]:
                    for item in reading["data"]:
                        station = stations[item["stationId"]]
                        writer.writerow([
                            reading["timestamp"], item["stationId"],
                            station["name"],
                            station["location"]["latitude"],
                            station["location"]["longitude"],
                            item["value"],
                        ])
                token = data.get("paginationToken")
                if not token:
                    break
                params = {"date": day.isoformat(), "paginationToken": token}
            print(f"Rainfall done: {day}")
    print(f"Saved: {path}")


def download_carpark():
    path = OUTPUT / f"carpark_{START:%Y%m%d}_{END:%Y%m%d}.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["snapshot_time", "carpark_number", "lot_type",
                         "lots_available", "total_lots", "update_datetime"])
        for day in days():
            for hour in range(0, 24, CARPARK_EVERY_HOURS):
                # The API returns the latest snapshot before this time on the
                # same day, so HH:00 would return nothing at midnight
                moment = datetime(day.year, day.month, day.day, hour, 1)
                data = get_json(CARPARK_URL,
                                {"date_time": moment.isoformat()})
                if not data["items"]:
                    print(f"No carpark data for {moment}")
                for item in data["items"]:
                    for carpark in item.get("carpark_data", []):
                        for lot in carpark["carpark_info"]:
                            writer.writerow([
                                item["timestamp"], carpark["carpark_number"],
                                lot["lot_type"], lot["lots_available"],
                                lot["total_lots"], carpark["update_datetime"],
                            ])
            print(f"Carpark done: {day}")
    print(f"Saved: {path}")


download_rainfall()
download_carpark()
print("Download completed.")
