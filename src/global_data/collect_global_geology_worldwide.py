
import time
import requests
import pandas as pd
from pathlib import Path

GRID_FILE = Path("data/processed/earth_grid.csv")
LAND_FILE = Path(
    "data/processed/land_classification/global_land_classification.csv"
)

# Keep worldwide results separate from the original pilot
OUTPUT_DIR = Path("data/processed/global_geology_worldwide")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

grid = pd.read_csv(GRID_FILE)
land = pd.read_csv(LAND_FILE)

# Keep only grid centres classified as land
land_grid = grid.merge(
    land[["cell_id", "land_class"]],
    on="cell_id",
    how="inner"
)

land_grid = land_grid[
    land_grid["land_class"] == "land"
].copy()

land_grid = land_grid.sort_values("cell_id").reset_index(drop=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "TERRATIME4D-Earth-Geology-Research/1.0"
})

cell_results = []
geology_records = []

print("STARTING WORLDWIDE LAND GEOLOGY COLLECTION")
print("Land grid centres available:", len(land_grid))

for index, cell in land_grid.iterrows():
    cell_id = int(cell["cell_id"])
    latitude = float(cell["latitude"])
    longitude = float(cell["longitude"])

    try:
        response = session.get(
            "https://macrostrat.org/api/v2/geologic_units/map",
            params={"lat": latitude, "lng": longitude},
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        success = result.get("success", {})
        records = success.get("data", [])

        if not isinstance(records, list):
            raise ValueError("Unexpected API response")

        cell_results.append({
            "cell_id": cell_id,
            "latitude": latitude,
            "longitude": longitude,
            "land_class": "land",
            "status": "success",
            "record_count": len(records)
        })

        for record in records:
            geology_records.append({
                "cell_id": cell_id,
                "latitude": latitude,
                "longitude": longitude,
                "map_id": record.get("map_id"),
                "name": record.get("name"),
                "lithology": record.get("lith"),
                "top_age_ma": record.get("t_age"),
                "bottom_age_ma": record.get("b_age"),
                "geological_period": record.get("best_int_name"),
                "source_id": record.get("source_id")
            })

        print(
            f"[{index + 1}/{len(land_grid)}] "
            f"Cell {cell_id}: {len(records)} records"
        )

    except Exception as error:
        cell_results.append({
            "cell_id": cell_id,
            "latitude": latitude,
            "longitude": longitude,
            "land_class": "land",
            "status": f"error: {error}",
            "record_count": 0
        })

        print(
            f"[{index + 1}/{len(land_grid)}] "
            f"Cell {cell_id}: ERROR - {error}"
        )

    # Save progress every 25 cells so partial results are preserved
    if (index + 1) % 25 == 0:
        pd.DataFrame(cell_results).to_csv(
            OUTPUT_DIR / "worldwide_geology_cell_status.csv",
            index=False
        )
        pd.DataFrame(geology_records).to_csv(
            OUTPUT_DIR / "worldwide_geology_records.csv",
            index=False
        )
        print("Progress saved.")

    # Be respectful of the public API
    time.sleep(1)

# Final save
pd.DataFrame(cell_results).to_csv(
    OUTPUT_DIR / "worldwide_geology_cell_status.csv",
    index=False
)

pd.DataFrame(geology_records).to_csv(
    OUTPUT_DIR / "worldwide_geology_records.csv",
    index=False
)

status_df = pd.DataFrame(cell_results)

print("\nWORLDWIDE GEOLOGY COLLECTION COMPLETE")
print("Land cells attempted:", len(cell_results))
print("Successful cells:", (status_df["status"] == "success").sum())
print("Failed cells:", status_df["status"].str.startswith("error").sum())
print("Geological records:", len(geology_records))
print("Output folder:", OUTPUT_DIR)
