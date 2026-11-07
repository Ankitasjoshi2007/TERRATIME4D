from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dem_quality_report.csv"
)


def inspect_tile(file_path):
    """Inspect DEM values, spatial metadata and approximate resolution."""

    try:
        with rasterio.open(file_path) as dataset:

            elevation = dataset.read(1, masked=True).astype("float64")

            values = elevation.compressed()
            values = values[np.isfinite(values)]

            bounds = dataset.bounds
            transform = dataset.transform

            center_latitude = (
                bounds.bottom + bounds.top
            ) / 2

            # Approximate conversion from geographic degrees to metres.
            pixel_width_m = (
                abs(transform.a)
                * 111320
                * np.cos(np.radians(center_latitude))
            )

            pixel_height_m = abs(transform.e) * 111320

            tags = dataset.tags()

            if len(values) == 0:
                return {
                    "file": file_path.name,
                    "status": "NO VALID DATA"
                }

            zero_count = int(np.count_nonzero(values == 0))

            return {
                "file": file_path.name,
                "status": "CHECKED",

                # Raster dimensions
                "width_pixels": dataset.width,
                "height_pixels": dataset.height,
                "band_count": dataset.count,

                # Coordinate reference system
                "crs": str(dataset.crs),

                # Geographic coverage
                "west": round(bounds.left, 6),
                "south": round(bounds.bottom, 6),
                "east": round(bounds.right, 6),
                "north": round(bounds.top, 6),

                # Native raster resolution
                "pixel_width_native": abs(transform.a),
                "pixel_height_native": abs(transform.e),
                "native_resolution_unit": (
                    "degrees" if dataset.crs and dataset.crs.is_geographic
                    else "CRS units"
                ),

                # Approximate ground resolution
                "pixel_width_m_approx": round(
                    float(pixel_width_m), 2
                ),
                "pixel_height_m_approx": round(
                    float(pixel_height_m), 2
                ),

                # Elevation quality
                "valid_pixels": int(len(values)),
                "nodata_value": dataset.nodata,
                "zero_pixels": zero_count,
                "zero_percent": round(
                    100 * zero_count / len(values), 2
                ),

                "minimum_m": round(float(values.min()), 2),
                "maximum_m": round(float(values.max()), 2),
                "average_m": round(float(values.mean()), 2),

                # Dataset metadata, when provided
                "dataset_tags": str(tags)
            }

    except Exception as error:
        return {
            "file": file_path.name,
            "status": "ERROR",
            "error": str(error)
        }


def main():

    files = sorted(DATA_FOLDER.glob("*.tif"))

    results = []

    print("\nTERRATIME 4D - DEM QUALITY AND METADATA CHECK")
    print("---------------------------------------------")

    if not files:
        print("No DEM files found:", DATA_FOLDER)
        return

    for file_path in files:

        result = inspect_tile(file_path)

        results.append(result)

        print("\nTile:", file_path.name)
        print("Status:", result["status"])

        if result["status"] == "CHECKED":

            print("CRS:", result["crs"])

            print(
                "Dimensions:",
                result["width_pixels"],
                "x",
                result["height_pixels"]
            )

            print(
                "Approximate pixel size:",
                result["pixel_width_m_approx"],
                "x",
                result["pixel_height_m_approx"],
                "metres"
            )

            print(
                "Elevation range:",
                result["minimum_m"],
                "to",
                result["maximum_m"],
                "metres"
            )

        elif result["status"] == "ERROR":
            print("Error:", result["error"])

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    successful = sum(
        result["status"] == "CHECKED"
        for result in results
    )

    print("\nTiles checked:", successful, "/", len(files))

    print("\nQuality report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()