from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

DATA_FOLDER = Path("data/raw/earth")
OUTPUT_FILE = Path("data/processed/srtm_slope_summary.csv")


def calculate_slope(file_path):
    with rasterio.open(file_path) as dataset:
        elevation = dataset.read(1, masked=True).astype("float64")
        elevation = elevation.filled(np.nan)

        # Find the approximate centre latitude of the tile
        latitude = (dataset.bounds.bottom + dataset.bounds.top) / 2

        # Calculate actual approximate pixel dimensions in metres
        transform = dataset.transform
        pixel_width = (
            abs(transform.a) * 111320 * np.cos(np.radians(latitude))
        )
        pixel_height = abs(transform.e) * 111320

        # Calculate elevation gradients
        dy, dx = np.gradient(
            elevation,
            pixel_height,
            pixel_width
        )

        slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))

        # Ignore invalid pixels when calculating statistics
        valid_slope = slope[np.isfinite(slope)]

        return {
            "file": file_path.name,
            "pixel_width_m": round(pixel_width, 2),
            "pixel_height_m": round(pixel_height, 2),
            "valid_pixels": len(valid_slope),
            "minimum_slope_degrees": round(float(valid_slope.min()), 2),
            "maximum_slope_degrees": round(float(valid_slope.max()), 2),
            "average_slope_degrees": round(float(valid_slope.mean()), 2)
        }


def main():
    hgt_files = sorted(
        file for file in DATA_FOLDER.rglob("*.hgt")
        if file.is_file()
    )

    results = []

    for file_path in hgt_files:
        result = calculate_slope(file_path)
        results.append(result)

        print("\nTERRAIN SLOPE ANALYSIS")
        print("---------------------")
        for key, value in result.items():
            print(f"{key}: {value}")

    if results:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        print("\nSlope summary saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()