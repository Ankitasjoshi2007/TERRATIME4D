
from pathlib import Path
import math

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCATIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_sample_locations.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "known_location_availability.csv"
)

BASE_URL = (
    "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"
)


def make_tile_name(latitude, longitude):
    """Build a one-degree Copernicus tile name from coordinates."""

    lat_degree = math.floor(latitude)
    lon_degree = math.floor(longitude)

    lat_direction = "N" if lat_degree >= 0 else "S"
    lon_direction = "E" if lon_degree >= 0 else "W"

    lat_text = f"{abs(lat_degree):02d}"
    lon_text = f"{abs(lon_degree):03d}"

    return (
        f"Copernicus_DSM_COG_30_"
        f"{lat_direction}{lat_text}_00_"
        f"{lon_direction}{lon_text}_00_DEM"
    )


def check_tile(session, tile_name):
    url = f"{BASE_URL}/{tile_name}/{tile_name}.tif"

    try:
        response = session.head(
            url,
            timeout=(10, 20),
            allow_redirects=True
        )

        if response.status_code == 200:
            return "Available"

        if response.status_code == 404:
            return "Not available"

        return f"HTTP {response.status_code}"

    except requests.RequestException as error:
        print(f"Request error: {error}")
        return "Request failed"


def main():
    print("\nTERRATIME 4D - KNOWN LOCATION TEST")
    print("----------------------------------")

    if not LOCATIONS_FILE.exists():
        raise FileNotFoundError(
            f"Locations file not found: {LOCATIONS_FILE}"
        )

    locations = pd.read_csv(LOCATIONS_FILE)
    results = []

    with requests.Session() as session:
        for _, row in locations.iterrows():

            tile_name = make_tile_name(
                row["target_latitude"],
                row["target_longitude"]
            )

            print(f"\nLocation: {row['location']}")
            print(f"Tile: {tile_name}")

            status = check_tile(session, tile_name)

            print(f"Result: {status}")

            results.append({
                "location": row["location"],
                "target_latitude": row["target_latitude"],
                "target_longitude": row["target_longitude"],
                "tile_name": tile_name,
                "availability": status
            })

    result_df = pd.DataFrame(results)
    result_df.to_csv(OUTPUT_FILE, index=False)

    print("\nTest completed.")
    print(result_df.to_string(index=False))
    print(f"\nReport saved to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
