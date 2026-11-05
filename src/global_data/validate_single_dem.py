from pathlib import Path
import rasterio
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TILE_NAME = "Copernicus_DSM_COG_30_S89_00_E016_00_DEM"

DEM_FILE = (
    PROJECT_ROOT
    / "data"
    / "copernicus_glo90"
    / f"{TILE_NAME}.tif"
)


def main():

    print("\nTERRATIME 4D - DEM VALIDATION")
    print("-----------------------------")

    if not DEM_FILE.exists():
        print("DEM file not found!")
        return

    try:
        with rasterio.open(DEM_FILE) as dem:

            elevation = dem.read(1, masked=True)
            valid = elevation.compressed()

            print("File readable: Yes")
            print("CRS:", dem.crs)
            print("Width:", dem.width)
            print("Height:", dem.height)
            print("Resolution:", dem.res)
            print("Data type:", dem.dtypes[0])
            print("NoData value:", dem.nodata)
            print("Valid pixels:", len(valid))

            if len(valid) > 0:
                print("Minimum elevation:", float(np.min(valid)))
                print("Maximum elevation:", float(np.max(valid)))
                print("Mean elevation:", float(np.mean(valid)))
            else:
                print("No valid elevation pixels found!")

            print("\nGeoTIFF validation completed.")

    except Exception as error:
        print("Validation failed:", error)


if __name__ == "__main__":
    main()