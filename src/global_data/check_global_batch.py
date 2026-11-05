
from pathlib import Path
import time

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_dem_inventory.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_availability_batch_001.csv"
)

BASE_URL = (
    "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"
)

BATCH_SIZE = 100
PAUSE_SECONDS = 0.2


def check_tile(session, tile_name):
    url = f"{BASE_URL}/{tile_name}/{tile_name}.tif"

    try:
        response = session.head(
            url,
            timeout=(10, 20),
            allow_redirects=True
        )

        if response.status_code == 200:
            return "Available", 200

        if response.status_code == 404:
            return "Not available", 404

        return "Inconclusive", response.status_code

    except requests.RequestException as error:
        print(f"Request error for {tile_name}: {error}")
        return "Request failed", None


def main():
    print("\nTERRATIME 4D - GLOBAL DEM BATCH 001")
    print("-----------------------------------")

    if not INVENTORY_FILE.exists():
        raise FileNotFoundError(
            f"Inventory not found: {INVENTORY_FILE}"
        )

    inventory = pd.read_csv(INVENTORY_FILE)

    if len(inventory) < BATCH_SIZE:
        raise ValueError(
            f"Inventory has fewer than {BATCH_SIZE} rows."
        )

    # Select the first 100 candidate tiles.
    batch = inventory.head(BATCH_SIZE).copy()

    results = []

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "TerraTime4D-Research/1.0"
        })

        for number, (_, row) in enumerate(
            batch.iterrows(),
            start=1
        ):
            tile_name = row["tile_name"]

            print(
                f"[{number}/{BATCH_SIZE}] "
                f"Checking {tile_name}...",
                end=" "
            )

            status, http_code = check_tile(
                session,
                tile_name
            )

            print(status)

            results.append({
                "cell_id": row["cell_id"],
                "tile_latitude": row["tile_latitude"],
                "tile_longitude": row["tile_longitude"],
                "tile_name": tile_name,
                "availability": status,
                "http_status": http_code
            })

            time.sleep(PAUSE_SECONDS)

    result_df = pd.DataFrame(results)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nBATCH TEST COMPLETED")
    print("--------------------")
    print("Tiles checked:", len(result_df))
    print(
        "Available:",
        (result_df["availability"] == "Available").sum()
    )
    print(
        "Not available:",
        (result_df["availability"] == "Not available").sum()
    )
    print(
        "Inconclusive or failed:",
        (~result_df["availability"].isin(
            ["Available", "Not available"]
        )).sum()
    )

    print("\nReport saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
