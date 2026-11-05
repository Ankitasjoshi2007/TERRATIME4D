from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_official_dem_inventory.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_dem_download_plan.csv"
)

RAW_DEM_DIR = (
    PROJECT_ROOT
    / "data"
    / "copernicus_glo90"
)


def main():
    print("\nTERRATIME 4D - DEM DOWNLOAD PLAN")
    print("--------------------------------")

    inventory = pd.read_csv(INVENTORY_FILE)

    RAW_DEM_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    existing_tiles = set()

    for tif_file in RAW_DEM_DIR.rglob("*.tif"):
        existing_tiles.add(tif_file.stem)

    inventory["local_status"] = inventory["tile_name"].apply(
        lambda name: (
            "Already downloaded"
            if name in existing_tiles
            else "Not downloaded"
        )
    )

    inventory["download_priority"] = "Candidate"

    inventory.loc[
        inventory["local_status"] == "Already downloaded",
        "download_priority"
    ] = "Complete"

    inventory.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Official tiles:", len(inventory))

    print(
        "Already downloaded:",
        (
            inventory["local_status"]
            == "Already downloaded"
        ).sum()
    )

    print(
        "Not downloaded:",
        (
            inventory["local_status"]
            == "Not downloaded"
        ).sum()
    )

    print("\nDownload plan saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()