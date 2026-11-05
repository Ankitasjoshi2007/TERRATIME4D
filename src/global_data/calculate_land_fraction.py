
from pathlib import Path

import pandas as pd
from global_land_mask import globe


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_land_diversity_sample_plan.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_land_fraction.csv"
)

# Sample each tile at a 10 x 10 grid of points.
GRID_SIZE = 10


def calculate_land_fraction(latitude, longitude):
    latitudes = [
        latitude + (i + 0.5) / GRID_SIZE
        for i in range(GRID_SIZE)
    ]

    longitudes = [
        longitude + (j + 0.5) / GRID_SIZE
        for j in range(GRID_SIZE)
    ]

    land_count = 0
    total_count = 0

    for lat in latitudes:
        for lon in longitudes:
            if lat >= 90 or lon >= 180:
                continue

            if globe.is_land(lat, lon):
                land_count += 1

            total_count += 1

    if total_count == 0:
        return 0.0

    return land_count / total_count


def main():
    print("\nTERRATIME 4D - LAND FRACTION ANALYSIS")
    print("-------------------------------------")

    sample = pd.read_csv(INPUT_FILE)

    results = []

    for _, tile in sample.iterrows():
        fraction = calculate_land_fraction(
            tile["tile_latitude"],
            tile["tile_longitude"]
        )

        results.append(fraction)

    sample["land_fraction"] = results
    sample["land_percentage"] = (
        sample["land_fraction"] * 100
    ).round(2)

    sample["land_category"] = sample[
        "land_percentage"
    ].apply(
        lambda x: (
            "Mostly land" if x >= 80
            else "Mixed land and water" if x >= 20
            else "Mostly water"
        )
    )

    sample.to_csv(OUTPUT_FILE, index=False)

    print("Tiles analyzed:", len(sample))

    print("\nLand category summary:")
    print(sample["land_category"].value_counts().to_string())

    print("\nAverage land percentage:")
    print(round(sample["land_percentage"].mean(), 2), "%")

    print("\nFirst 10 results:")
    print(
        sample[
            [
                "tile_name",
                "land_percentage",
                "land_category"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nResults saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
