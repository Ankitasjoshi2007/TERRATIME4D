from pathlib import Path
import math
import requests
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "global_sample_locations.csv"
)

OUTPUT_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

BASE_URL = (
    "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"
)


def create_tile_name(latitude, longitude):
    lat_degree = math.floor(latitude)
    lon_degree = math.floor(longitude)

    north_south = "N" if lat_degree >= 0 else "S"
    east_west = "E" if lon_degree >= 0 else "W"

    tile_name = (
        f"Copernicus_DSM_COG_30_"
        f"{north_south}{abs(lat_degree):02d}_00_"
        f"{east_west}{abs(lon_degree):03d}_00_DEM"
    )

    return tile_name


def download_tile(latitude, longitude):
    tile_name = create_tile_name(latitude, longitude)

    url = f"{BASE_URL}/{tile_name}/{tile_name}.tif"

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_FOLDER / f"{tile_name}.tif"

    if output_file.exists():
        print("Already downloaded:", tile_name)
        return "Already downloaded"

    try:
        response = requests.get(url, stream=True, timeout=60)

        if response.status_code == 404:
            print("Tile not found:", tile_name)
            return "Not available"

        response.raise_for_status()

        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

        print("Downloaded:", tile_name)
        return "Downloaded"

    except requests.RequestException as error:
        if output_file.exists():
            output_file.unlink()

        print("Download failed:", tile_name, error)
        return "Failed"


def main():
    if not INPUT_FILE.exists():
        print("Location CSV not found:", INPUT_FILE)
        return

    locations = pd.read_csv(INPUT_FILE)

    print("\nTERRATIME 4D - COPERNICUS GLOBAL COLLECTOR")
    print("------------------------------------------")
    print("Locations to process:", len(locations))

    results = []

    for _, location in locations.iterrows():
        name = location["location"]
        latitude = float(location["target_latitude"])
        longitude = float(location["target_longitude"])

        print(f"\nProcessing: {name}")

        tile_name = create_tile_name(latitude, longitude)
        status = download_tile(latitude, longitude)

        results.append({
            "location": name,
            "latitude": latitude,
            "longitude": longitude,
            "tile_name": tile_name,
            "status": status
        })

    summary = pd.DataFrame(results)

    summary_file = (
        PROJECT_ROOT / "data" / "processed"
        / "copernicus_download_summary.csv"
    )

    summary.to_csv(summary_file, index=False)

    print("\nDownload summary saved to:", summary_file)
    print("\n", summary.to_string(index=False))


if __name__ == "__main__":
    main()