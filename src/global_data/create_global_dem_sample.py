
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_official_dem_inventory.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_sample_plan.csv"
)

SAMPLE_SIZE = 500
RANDOM_STATE = 42


def assign_latitude_band(latitude):
    if -90 <= latitude < -60:
        return "60S to 90S"
    elif -60 <= latitude < -30:
        return "30S to 60S"
    elif -30 <= latitude < 0:
        return "0 to 30S"
    elif 0 <= latitude < 30:
        return "0 to 30N"
    elif 30 <= latitude < 60:
        return "30N to 60N"
    elif 60 <= latitude <= 90:
        return "60N to 90N"
    return "Outside range"


def main():
    print("\nTERRATIME 4D - STRATIFIED GLOBAL DEM SAMPLE")
    print("-------------------------------------------")

    inventory = pd.read_csv(INPUT_FILE)

    if inventory.empty:
        raise ValueError("Official DEM inventory is empty.")

    inventory["latitude_band"] = inventory[
        "tile_latitude"
    ].apply(assign_latitude_band)

    # Remove rows outside the expected latitude range.
    inventory = inventory[
        inventory["latitude_band"] != "Outside range"
    ].copy()

    band_counts = inventory["latitude_band"].value_counts()

    # Allocate sample tiles proportionally to the number
    # of official tiles in each latitude band.
    allocation = (
        band_counts / band_counts.sum() * min(
            SAMPLE_SIZE, len(inventory)
        )
    ).round().astype(int)

    # Correct rounding so the total equals SAMPLE_SIZE.
    target_size = min(SAMPLE_SIZE, len(inventory))

    while allocation.sum() > target_size:
        band = allocation.idxmax()
        allocation[band] -= 1

    while allocation.sum() < target_size:
        band = (band_counts - allocation).idxmax()
        allocation[band] += 1

    samples = []

    for band, count in allocation.items():
        band_data = inventory[
            inventory["latitude_band"] == band
        ]

        if count > 0:
            selected = band_data.sample(
                n=min(count, len(band_data)),
                random_state=RANDOM_STATE
            )
            samples.append(selected)

    sample = pd.concat(
        samples,
        ignore_index=True
    )

    sample = sample.sort_values(
        ["tile_latitude", "tile_longitude"]
    ).reset_index(drop=True)

    sample["sample_id"] = range(1, len(sample) + 1)
    sample["download_status"] = "Planned"

    columns = [
        "sample_id",
        "cell_id",
        "tile_latitude",
        "tile_longitude",
        "tile_name",
        "latitude_band",
        "download_status",
    ]

    sample[columns].to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Official inventory tiles:", len(inventory))
    print("Stratified sample size:", len(sample))

    print("\nSample allocation by latitude band:")
    print(
        sample["latitude_band"]
        .value_counts()
        .reindex(band_counts.index, fill_value=0)
        .to_string()
    )

    print("\nFirst 10 sample tiles:")
    print(sample[columns].head(10).to_string(index=False))

    print("\nSample plan saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
