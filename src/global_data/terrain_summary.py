from pathlib import Path
import numpy as np
import pandas as pd
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "global_terrain_features.csv"


def analyze_tile(file_path):
    with rasterio.open(file_path) as dataset:
        elevation = dataset.read(1).astype("float64")

        latitude = (dataset.bounds.bottom + dataset.bounds.top) / 2

        # Convert geographic pixel spacing approximately into metres.
        pixel_width = (
            abs(dataset.transform.a)
            * 111320
            * np.cos(np.radians(latitude))
        )
        pixel_height = abs(dataset.transform.e) * 111320

        # Provisional valid-land mask.
        land_mask = np.isfinite(elevation)

        if "N19_00_W155" in file_path.name:
            land_mask &= elevation > 1.0

        # Calculate slope in degrees.
        dy, dx = np.gradient(elevation, pixel_height, pixel_width)
        slope = np.degrees(
            np.arctan(np.sqrt(dx**2 + dy**2))
        )

        land_elevation = elevation[land_mask]
        land_slope = slope[land_mask]

        if len(land_elevation) == 0:
            return None

        return {
            "location_tile": file_path.stem,
            "land_pixels": len(land_elevation),
            "minimum_elevation_m": round(float(land_elevation.min()), 2),
            "maximum_elevation_m": round(float(land_elevation.max()), 2),
            "average_elevation_m": round(float(land_elevation.mean()), 2),
            "average_slope_degrees": round(float(land_slope.mean()), 2),
            "maximum_slope_degrees": round(float(land_slope.max()), 2),
            "pixel_width_m_approx": round(pixel_width, 2),
            "pixel_height_m_approx": round(pixel_height, 2)
        }


def main():
    files = sorted(DATA_FOLDER.glob("*.tif"))
    results = []

    print("\nTERRATIME 4D - GLOBAL TERRAIN FEATURES")
    print("-------------------------------------")

    for file_path in files:
        result = analyze_tile(file_path)

        if result:
            results.append(result)
            print("\nProcessed:", file_path.name)
            print("Average elevation:", result["average_elevation_m"], "m")
            print("Average slope:", result["average_slope_degrees"], "degrees")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)

    print("\nTerrain feature report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()