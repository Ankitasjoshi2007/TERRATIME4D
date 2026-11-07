
from pathlib import Path

import rasterio


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
EARTH_FOLDER = PROJECT_ROOT / "data" / "raw" / "earth"

SRTM_FILENAMES = [
    "N12E077.hgt",
    "N13E077.hgt",
]


def find_srtm_file(filename):
    """Search for an HGT file anywhere inside the Earth data folder."""
    matches = list(EARTH_FOLDER.rglob(filename))

    if len(matches) == 0:
        print(f"ERROR: {filename} was not found.")
        return None

    if len(matches) > 1:
        print(f"ERROR: Multiple copies of {filename} were found:")
        for match in matches:
            print(match)
        return None

    return matches[0]


def validate_srtm(filename):
    print("\nNASA SRTM VALIDATION")
    print("--------------------")
    print(f"File: {filename}")

    dem_path = find_srtm_file(filename)

    if dem_path is None:
        return False

    print(f"Location: {dem_path}")

    try:
        with rasterio.open(dem_path) as dem:
            data = dem.read(1, masked=True)

            valid_pixels = int(data.count())
            total_pixels = int(data.size)
            invalid_pixels = total_pixels - valid_pixels

            print(f"Readable: Yes")
            print(f"Dimensions: {dem.width} x {dem.height}")
            print(f"CRS: {dem.crs}")
            print(f"Resolution: {dem.res}")
            print(f"Bounds: {dem.bounds}")
            print(f"Data type: {dem.dtypes[0]}")
            print(f"NoData value: {dem.nodata}")
            print(f"Valid pixels: {valid_pixels}")
            print(f"Invalid pixels: {invalid_pixels}")

            if valid_pixels == 0:
                print("RESULT: CHECK REQUIRED - no valid pixels")
                return False

            print("\nELEVATION STATISTICS")
            print(f"Minimum elevation: {float(data.min())} m")
            print(f"Maximum elevation: {float(data.max())} m")
            print(f"Mean elevation: {float(data.mean())} m")
            print(f"Standard deviation: {float(data.std())} m")

            shape_ok = dem.width == 3601 and dem.height == 3601
            crs_ok = dem.crs is not None
            resolution_ok = dem.res[0] > 0 and dem.res[1] > 0

            print("\nQUALITY CHECKS")
            print(f"Expected 3601 x 3601 dimensions: {shape_ok}")
            print(f"CRS available: {crs_ok}")
            print(f"Positive resolution: {resolution_ok}")

            passed = (
                shape_ok
                and crs_ok
                and resolution_ok
                and valid_pixels > 0
            )

            print(
                "RESULT: PASSED"
                if passed
                else "RESULT: CHECK REQUIRED"
            )

            return passed

    except Exception as error:
        print(f"ERROR: Could not validate file: {error}")
        return False


if __name__ == "__main__":
    if not EARTH_FOLDER.exists():
        print(f"ERROR: Earth data folder not found: {EARTH_FOLDER}")
    else:
        results = [
            validate_srtm(filename)
            for filename in SRTM_FILENAMES
        ]

        print("\nOVERALL RESULT")
        print("--------------")
        print(
            "BOTH TILES PASSED"
            if all(results)
            else "ONE OR MORE TILES NEED CHECKING"
        )
