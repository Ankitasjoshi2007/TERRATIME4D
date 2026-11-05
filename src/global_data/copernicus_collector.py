from pathlib import Path
import math
import requests
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_sample_locations.csv"
)

OUTPUT_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "copernicus_glo90"
)

BASE_URL = (
    "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"
)

SUMMARY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_download_summary.csv"
)


def create_tile_name(latitude, longitude):
    """Create a Copernicus GLO-90 tile name."""

    if not -90 <= latitude <= 90:
        raise ValueError(f"Invalid latitude: {latitude}")

    if not -180 <= longitude <= 180:
        raise ValueError(f"Invalid longitude: {longitude}")

    lat_degree = math.floor(latitude)
    lon_degree = math.floor(longitude)

    north_south = "N" if lat_degree >= 0 else "S"
    east_west = "E" if lon_degree >= 0 else "W"

    return (
        f"Copernicus_DSM_COG_30_"
        f"{north_south}{abs(lat_degree):02d}_00_"
        f"{east_west}{abs(lon_degree):03d}_00_DEM"
    )


def download_tile(latitude, longitude):
    """Download one DEM tile safely."""

    tile_name = create_tile_name(latitude, longitude)

    url = f"{BASE_URL}/{tile_name}/{tile_name}.tif"

    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = OUTPUT_FOLDER / f"{tile_name}.tif"
    temporary_file = OUTPUT_FOLDER / f"{tile_name}.tif.part"

    if output_file.exists():
        print("Already downloaded:", tile_name)
        return "Already downloaded"

    try:
        with requests.get(
            url,
            stream=True,
            timeout=(15, 120)
        ) as response:

            if response.status_code == 404:
                print("Tile not found:", tile_name)
                return "Not available"

            response.raise_for_status()

            with open(temporary_file, "wb") as file:
                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        file.write(chunk)

        if not temporary_file.exists() or temporary_file.stat().st_size == 0:
            raise IOError("Downloaded file is empty.")

        temporary_file.replace(output_file)

        print("Downloaded:", tile_name)
        return "Downloaded"

    except (requests.RequestException, OSError) as error:

        if temporary_file.exists():
            temporary_file.unlink()

        print("Download failed:", tile_name, error)
        return "Failed"


def main():

    print("\nTERRATIME 4D - COPERNICUS DEM COLLECTOR")
    print("---------------------------------------")

    if not INPUT_FILE.exists():
        print("Location CSV not found:", INPUT_FILE)
        return

    locations = pd.read_csv(INPUT_FILE)

    required_columns = {
        "location",
        "target_latitude",
        "target_longitude"
    }

    if not required_columns.issubset(locations.columns):
        raise ValueError(
            "Input CSV must contain: "
            "location, target_latitude, target_longitude"
        )

    print("Locations to process:", len(locations))

    results = []

    for _, location in locations.iterrows():

        name = location["location"]
        latitude = float(location["target_latitude"])
        longitude = float(location["target_longitude"])

        print(f"\nProcessing: {name}")

        tile_name = create_tile_name(latitude, longitude)

        status = download_tile(
            latitude,
            longitude
        )

        results.append({
            "location": name,
            "latitude": latitude,
            "longitude": longitude,
            "tile_name": tile_name,
            "status": status
        })

    summary = pd.DataFrame(results)

    SUMMARY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    print("\nDownload summary saved to:")
    print(SUMMARY_FILE)

    print("\n", summary.to_string(index=False))


if __name__ == "__main__":
    main()