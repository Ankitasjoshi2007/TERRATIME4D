
import time
import requests
import pandas as pd
from pathlib import Path

GRID_FILE = Path("data/processed/earth_grid.csv")
OUTPUT_DIR = Path("data/processed/global_geology")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

grid = pd.read_csv(GRID_FILE)

# Six latitude bands and four longitude regions
latitude_bands = [
    (-90, -60), (-60, -30), (-30, 0),
    (0, 30), (30, 60), (60, 90)
]

longitude_regions = [
    (-180, -90), (-90, 0), (0, 90), (90, 180)
]

sample = []

for lat_min, lat_max in latitude_bands:
    for lon_min, lon_max in longitude_regions:
        candidates = grid[
            (grid["latitude"] >= lat_min) &
            (grid["latitude"] < lat_max) &
            (grid["longitude"] >= lon_min) &
            (grid["longitude"] < lon_max)
        ]

        if not candidates.empty:
            # Select the middle grid cell in this region
            cell = candidates.iloc[len(candidates) // 2]
            sample.append(cell)

session = requests.Session()
cell_results = []
geology_records = []

print("Starting improved global geology pilot...")
print("Cells selected:", len(sample))

for cell in sample:
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
            f"Cell {cell_id}: "
            f"{latitude}, {longitude} - "
            f"{len(records)} records"
        )

    except Exception as error:
        cell_results.append({
            "cell_id": cell_id,
            "latitude": latitude,
            "longitude": longitude,
            "status": f"error: {error}",
            "record_count": 0
        })
        print(f"Cell {cell_id}: ERROR - {error}")

    time.sleep(1)

pd.DataFrame(cell_results).to_csv(
    OUTPUT_DIR / "global_geology_cell_status.csv",
    index=False
)

pd.DataFrame(geology_records).to_csv(
    OUTPUT_DIR / "global_geology_records.csv",
    index=False
)

print("\nIMPROVED PILOT COMPLETE")
print("Cells tested:", len(cell_results))
print("Geological records:", len(geology_records))
print("Output folder:", OUTPUT_DIR)
