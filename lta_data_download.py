
import os
import csv
import requests
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # reads .env into environment variables
LTA_API_KEY = os.getenv("LTA_API_KEY")
if not LTA_API_KEY:
    raise SystemExit("LTA_API_KEY not found. Check your .env file")


BASE_URL = "https://datamall2.mytransport.sg/ltaodataservice"

OUTPUT = Path("CA1_Datasets")
OUTPUT.mkdir(exist_ok=True)

HEADERS = {
    "AccountKey": LTA_API_KEY,
    "accept": "application/json"
}

def get_json(endpoint, params=None):
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=HEADERS,
        params=params,
        timeout=60
    )
    response.raise_for_status()
    return response.json()

# 1. Download monthly Bus Origin-Destination ZIP
month = "202609"

data = get_json("PV/ODBus", {"Date": month})
records = data.get("value", [])

if not records or not records[0].get("Link"):
    raise RuntimeError(
        f"No download link returned for {month}: {data}"
    )

download_url = records[0]["Link"]

# Download immediately: link expires after 5 minutes
response = requests.get(download_url, timeout=120)
response.raise_for_status()

zip_path = OUTPUT / f"bus_od_{month}.zip"
zip_path.write_bytes(response.content)

print(f"Downloaded: {zip_path}")

# 2. Download all Bus Stops (500 records per request)
bus_stops = []
skip = 0

while True:
    data = get_json("BusStops", {"$skip": skip})
    batch = data.get("value", [])

    if not batch:
        break

    bus_stops.extend(batch)
    print(f"Retrieved {len(bus_stops)} bus stops")

    if len(batch) < 500:
        break

    skip += 500

# 3. Save Bus Stops as CSV
csv_path = OUTPUT / "bus_stops.csv"

columns = [
    "BusStopCode",
    "RoadName",
    "Description",
    "Latitude",
    "Longitude"
]

with csv_path.open(
    "w", newline="", encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(
        file, fieldnames=columns, extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(bus_stops)

print(f"Saved: {csv_path}")
print("Download completed.")
