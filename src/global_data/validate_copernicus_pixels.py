from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEM_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"


def main():
    files = sorted(DEM_FOLDER.rglob("*.tif"))

    print("\nTERRATIME 4D - COPERNICUS PIXEL VALIDATION")
    print("------------------------------------------")
    print("Total TIFF files:", len(files))

    for file_path in files:
        print("\nTile:", file_path.name)

        with rasterio.open(file_path) as dataset:
            elevation = dataset.read(1, masked=True)

            valid_count = int(elevation.count())

            print("Dimensions:", dataset.width, "x", dataset.height)
            print("CRS:", dataset.crs)
            print("NoData:", dataset.nodata)
            print("Valid pixels:", valid_count)
            print("Total pixels:", dataset.width * dataset.height)

            if valid_count > 0:
                print("Minimum elevation:", float(elevation.min()))
                print("Maximum elevation:", float(elevation.max()))
                print("Mean elevation:", float(elevation.mean()))
            else:
                print("WARNING: No valid elevation pixels!")

            print("Mask flags:", dataset.mask_flag_enums)


if __name__ == "__main__":
    main()
print("\nHAWAII OCEAN PIXEL CHECK")
print("------------------------")

hawaii_file = next(
    DEM_FOLDER.glob("*N19_00_W155_00_DEM.tif")
)

with rasterio.open(hawaii_file) as dataset:
    elevation = dataset.read(1)

    near_sea_level = int(np.count_nonzero(elevation <= 1))

    total_pixels = elevation.size

    percentage = (near_sea_level / total_pixels) * 100

    print("Pixels at or below 1 metre:", near_sea_level)
    print("Total pixels:", total_pixels)
    print("Percentage:", round(percentage, 2), "%")