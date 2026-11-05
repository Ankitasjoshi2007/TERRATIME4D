import argparse
from pathlib import Path

import rasterio
import numpy as np


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEM_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

# Keep the Antarctic tile as the default test tile
DEFAULT_TILE = "Copernicus_DSM_COG_30_S89_00_E016_00_DEM.tif"


def validate_dem(tile_name):
    # Add .tif if the user provides only the tile name
    if not tile_name.lower().endswith(".tif"):
        tile_name += ".tif"

    dem_path = DEM_FOLDER / tile_name

    print("\nTERRATIME 4D - DEM VALIDATION")
    print("--------------------------------")

    if not dem_path.exists():
        print(f"ERROR: DEM file not found: {dem_path}")
        return

    try:
        with rasterio.open(dem_path) as dem:
            data = dem.read(1, masked=True)

            print("File readable: Yes")
            print(f"File: {dem_path.name}")
            print(f"CRS: {dem.crs}")
            print(f"Width: {dem.width}")
            print(f"Height: {dem.height}")
            print(f"Resolution: {dem.res}")
            print(f"Bounds: {dem.bounds}")
            print(f"Data type: {dem.dtypes[0]}")
            print(f"NoData value: {dem.nodata}")

            valid_pixels = data.count()
            total_pixels = data.size
            invalid_pixels = total_pixels - valid_pixels

            print(f"Valid pixels: {valid_pixels}")
            print(f"Invalid pixels: {invalid_pixels}")

            # Grid checks
            pixel_width = abs(dem.transform.a)
            pixel_height = abs(dem.transform.e)

            geographic_width = dem.width * pixel_width
            geographic_height = dem.height * pixel_height

            width_ok = abs(geographic_width - 1.0) < 0.01
            height_ok = abs(geographic_height - 1.0) < 0.01
            resolution_ok = pixel_width > 0 and pixel_height > 0
            crs_ok = dem.crs is not None

            print("\nGRID CHECKS")
            print("------------")
            print(f"Width consistency: {width_ok}")
            print(f"Height consistency: {height_ok}")
            print(f"Positive pixel resolution: {resolution_ok}")
            print(f"CRS available: {crs_ok}")

            # Elevation statistics
            print("\nELEVATION STATISTICS")
            print("--------------------")

            if valid_pixels > 0:
                print(f"Minimum elevation: {float(data.min())}")
                print(f"Maximum elevation: {float(data.max())}")
                print(f"Mean elevation: {float(data.mean())}")
                print(f"Standard deviation: {float(data.std())}")
            else:
                print("ERROR: No valid elevation pixels found.")

            # Overall technical result
            checks_passed = (
                width_ok
                and height_ok
                and resolution_ok
                and crs_ok
                and valid_pixels > 0
            )

            print("\nVALIDATION RESULT")
            print("-----------------")
            print("PASSED" if checks_passed else "CHECK REQUIRED")

    except Exception as error:
        print(f"ERROR: Could not validate DEM: {error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate a downloaded Copernicus DEM tile."
    )

    parser.add_argument(
        "tile_name",
        nargs="?",
        default=DEFAULT_TILE,
        help="DEM filename, with or without the .tif extension."
    )

    args = parser.parse_args()
    validate_dem(args.tile_name)