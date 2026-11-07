
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_FILE = (
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
    / "copernicus_global_coverage.csv"
)


def main():
    print("\nTERRATIME 4D - OFFICIAL COVERAGE COMPARISON")
    print("-------------------------------------------")

    inventory = pd.read_csv(INVENTORY_FILE)

    official_tiles = {
        line.strip()
        for line in OFFICIAL_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    }

    inventory["officially_listed"] = (
        inventory["tile_name"].isin(official_tiles)
    )

    inventory["availability"] = inventory[
        "officially_listed"
    ].map({
        True: "Listed by provider",
        False: "Not listed by provider"
    })

    inventory.to_csv(
        OUTPUT_FILE,
        index=False
    )

    listed_count = inventory["officially_listed"].sum()
    not_listed_count = len(inventory) - listed_count

    print("Candidate tiles:", len(inventory))
    print("Official tile-list entries:", len(official_tiles))
    print("Candidates listed by provider:", listed_count)
    print("Candidates not listed:", not_listed_count)

    print("\nFirst 10 listed candidates:")
    print(
        inventory[
            inventory["officially_listed"]
        ][["tile_name", "availability"]]
        .head(10)
        .to_string(index=False)
    )

    print("\nCoverage report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
