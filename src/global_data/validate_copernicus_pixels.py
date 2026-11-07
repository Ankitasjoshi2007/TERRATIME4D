
from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEM_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "copernicus_glo90"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_pixel_validation_report.txt"
)


def main():

    files = sorted(DEM_FOLDER.rglob("*.tif"))

    print("\nTERRATIME 4D - COPERNICUS PIXEL VALIDATION")
    print("------------------------------------------")
    print("Total TIFF files:", len(files))

    report = []

    for file_path in files:

        print("\nTile:", file_path.name)

        try:
            with rasterio.open(file_path) as dataset:

                elevation = dataset.read(1, masked=True)

                valid_count = int(elevation.count())
                total_count = dataset.width * dataset.height

                if valid_count > 0:

                    minimum = float(elevation.min())
                    maximum = float(elevation.max())
                    mean = float(elevation.mean())

                    status = "PASS"

                else:
                    minimum = None
                    maximum = None
                    mean = None

                    status = "FAIL"

                print(
                    "Dimensions:",
                    dataset.width,
                    "x",
                    dataset.height
                )

                print("CRS:", dataset.crs)
                print("Bounds:", dataset.bounds)
                print("Resolution:", dataset.res)
                print("NoData:", dataset.nodata)

                print("Valid pixels:", valid_count)
                print("Total pixels:", total_count)

                print("Minimum elevation:", minimum)
                print("Maximum elevation:", maximum)
                print("Mean elevation:", mean)

                print("Mask flags:", dataset.mask_flag_enums)

                print("Validation:", status)

                report.append(
                    f"Tile: {file_path.name}\n"
                    f"Status: {status}\n"
                    f"Dimensions: {dataset.width} x {dataset.height}\n"
                    f"CRS: {dataset.crs}\n"
                    f"Bounds: {dataset.bounds}\n"
                    f"Resolution: {dataset.res}\n"
                    f"NoData: {dataset.nodata}\n"
                    f"Valid pixels: {valid_count}\n"
                    f"Total pixels: {total_count}\n"
                    f"Minimum elevation: {minimum}\n"
                    f"Maximum elevation: {maximum}\n"
                    f"Mean elevation: {mean}\n"
                    f"Mask flags: {dataset.mask_flag_enums}\n"
                    "------------------------------------------\n"
                )

        except Exception as error:

            print("VALIDATION ERROR:", error)

            report.append(
                f"Tile: {file_path.name}\n"
                f"Status: ERROR\n"
                f"Error: {error}\n"
                "------------------------------------------\n"
            )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\nVALIDATION COMPLETE")
    print("Report saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
