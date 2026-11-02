from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import generic_filter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "global_roughness_summary.csv"
)


def analyze_roughness(file_path):
    with rasterio.open(file_path) as dataset:
        elevation = dataset.read(1, masked=True).filled(np.nan)

        # Calculate local elevation variation in a 3 x 3 pixel window.
        def local_roughness(values):
            valid = values[np.isfinite(values)]

            if len(valid) < 5:
                return np.nan

            return float(np.std(valid))

        roughness = generic_filter(
            elevation,
            local_roughness,
            size=3,
            mode="nearest"
        )

        # Exclude ocean-dominated pixels for the Hawaii test tile.
        valid_mask = np.isfinite(roughness)

        if "N19_00_W155" in file_path.name:
            valid_mask &= elevation > 1.0

        values = roughness[valid_mask]

        if len(values) == 0:
            return None

        return {
            "tile": file_path.stem,
            "valid_pixels": len(values),
            "average_roughness_m": round(float(values.mean()), 2),
            "maximum_roughness_m": round(float(values.max()), 2),
            "minimum_roughness_m": round(float(values.min()), 2)
        }


def main():
    files = sorted(DATA_FOLDER.glob("*.tif"))
    results = []

    print("\nTERRATIME 4D - TERRAIN ROUGHNESS ANALYSIS")
    print("----------------------------------------")

    for file_path in files:
        result = analyze_roughness(file_path)

        if result:
            results.append(result)
            print("\nTile:", result["tile"])
            print("Average roughness:",
                  result["average_roughness_m"], "m")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)

    print("\nRoughness report saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()