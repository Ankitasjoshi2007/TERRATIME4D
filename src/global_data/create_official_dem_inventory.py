from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_dem_inventory.csv"
)

OFFICIAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_glo90_tileList.txt"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_official_dem_inventory.csv"
)


def main():
    print("\nTERRATIME 4D - OFFICIAL DEM INVENTORY")
    print("-------------------------------------")

    candidates = pd.read_csv(CANDIDATE_FILE)

    official_tiles = {
        line.strip()
        for line in OFFICIAL_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    }

    official_inventory = candidates[
        candidates["tile_name"].isin(official_tiles)
    ].copy()

    official_inventory = official_inventory.sort_values(
        ["tile_latitude", "tile_longitude"]
    ).reset_index(drop=True)

    official_inventory["availability"] = (
        "Listed by provider"
    )

    official_inventory["download_status"] = (
        "Not downloaded"
    )

    official_inventory.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nCandidate tiles:", len(candidates))
    print(
        "Official provider tiles:",
        len(official_tiles)
    )
    print(
        "Official tiles matched:",
        len(official_inventory)
    )

    print("\nColumns:")
    print(
        ", ".join(official_inventory.columns)
    )

    print("\nFirst 10 official tiles:")
    print(
        official_inventory.head(10).to_string(
            index=False
        )
    )

    print("\nOfficial inventory saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()