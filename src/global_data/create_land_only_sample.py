
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_land_fraction.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_land_only_sample.csv"
)

MIN_LAND_PERCENTAGE = 80


def main():
    print("\nTERRATIME 4D - LAND-FOCUSED DEM SAMPLE")
    print("--------------------------------------")

    data = pd.read_csv(INPUT_FILE)

    land_sample = data[
        data["land_percentage"] >= MIN_LAND_PERCENTAGE
    ].copy()

    land_sample = land_sample.sort_values(
        ["tile_latitude", "tile_longitude"]
    ).reset_index(drop=True)

    land_sample["land_sample_id"] = range(
        1, len(land_sample) + 1
    )

    land_sample["download_status"] = "Planned"

    land_sample.to_csv(OUTPUT_FILE, index=False)

    print("Original sample:", len(data))
    print("Land-focused tiles:", len(land_sample))
    print(
        "Minimum land percentage:",
        MIN_LAND_PERCENTAGE,
        "%"
    )

    print("\nLand tiles by latitude band:")
    print(
        land_sample["latitude_band"]
        .value_counts()
        .to_string()
    )

    print("\nFirst 10 selected tiles:")
    print(
        land_sample[
            [
                "tile_name",
                "land_percentage",
                "latitude_band",
                "longitude_band"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
