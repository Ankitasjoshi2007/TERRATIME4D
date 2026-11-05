
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
    / "global_dem_land_diversity_sample_plan.csv"
)

SAMPLE_SIZE = 100
RANDOM_STATE = 42


def main():
    print("\nTERRATIME 4D - GEOGRAPHICALLY BALANCED SAMPLE")
    print("---------------------------------------------")

    inventory = pd.read_csv(INPUT_FILE)

    if inventory.empty:
        raise ValueError("Official DEM inventory is empty.")

    latitude_bins = [-90, -60, -30, 0, 30, 60, 90]
    latitude_labels = [
        "60S to 90S",
        "30S to 60S",
        "0 to 30S",
        "0 to 30N",
        "30N to 60N",
        "60N to 90N",
    ]

    longitude_bins = [-180, -120, -60, 0, 60, 120, 180]
    longitude_labels = [
        "120W to 180W",
        "60W to 120W",
        "0 to 60W",
        "0 to 60E",
        "60E to 120E",
        "120E to 180E",
    ]

    inventory["latitude_band"] = pd.cut(
        inventory["tile_latitude"],
        bins=latitude_bins,
        labels=latitude_labels,
        include_lowest=True,
        right=False,
    )

    inventory["longitude_band"] = pd.cut(
        inventory["tile_longitude"],
        bins=longitude_bins,
        labels=longitude_labels,
        include_lowest=True,
        right=False,
    )

    inventory = inventory.dropna(
        subset=["latitude_band", "longitude_band"]
    ).copy()

    # Each occupied latitude-longitude combination is one zone.
    groups = {
        zone: group
        for zone, group in inventory.groupby(
            ["latitude_band", "longitude_band"],
            observed=True
        )
    }

    target_size = min(SAMPLE_SIZE, len(inventory))

    # Allocate tiles round-robin across occupied zones.
    allocation = {zone: 0 for zone in groups}
    remaining = target_size

    while remaining > 0:
        added_this_round = 0

        for zone, group in groups.items():
            if allocation[zone] < len(group):
                allocation[zone] += 1
                remaining -= 1
                added_this_round += 1

                if remaining == 0:
                    break

        if added_this_round == 0:
            break

    samples = []

    for zone, group in groups.items():
        count = allocation[zone]

        if count > 0:
            selected = group.sample(
                n=count,
                random_state=RANDOM_STATE
            )
            samples.append(selected)

    sample = pd.concat(samples, ignore_index=True)

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
        "longitude_band",
        "download_status",
    ]

    sample[columns].to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Official inventory tiles:", len(inventory))
    print("Geographic zones represented:", len(groups))
    print("Selected sample tiles:", len(sample))

    print("\nTiles selected per geographic zone:")
    print(
        sample.groupby(
            ["latitude_band", "longitude_band"],
            observed=True
        ).size().to_string()
    )

    print("\nSample plan saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
