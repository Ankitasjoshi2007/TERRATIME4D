
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import generic_filter


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_roughness_summary.csv"
)


def analyze_roughness(file_path):
    """Calculate local elevation variation using a 3 x 3 window."""

    with rasterio.open(file_path) as dataset:

        elevation = dataset.read(1, masked=True).astype("float64")
        elevation = elevation.filled(np.nan)

        # Exclude invalid elevation values.
        valid_mask = np.isfinite(elevation)

        # Provisional ocean exclusion for the Hawaii sample.
        if "N19_00_W155" in file_path.name:
            valid_mask &= elevation > 1.0

        if not np.any(valid_mask):
            return None

        # Exclude ocean and invalid cells before roughness calculation.
        elevation = np.where(valid_mask, elevation, np.nan)

        def local_roughness(values):
            valid = values[np.isfinite(values)]

            # Require at least five valid cells in the 3 x 3 window.
            if valid.size < 5:
                return np.nan

            return float(np.std(valid))

        roughness = generic_filter(
            elevation,
            local_roughness,
            size=3,
            mode="constant",
            cval=np.nan
        )

        # Retain only valid land pixels with valid roughness.
        roughness_mask = valid_mask & np.isfinite(roughness)

        values = roughness[roughness_mask]

        if values.size == 0:
            return None

        return {
            "tile": file_path.stem,
            "valid_pixels": int(values.size),
            "average_roughness_m": round(
                float(values.mean()), 2
            ),
            "maximum_roughness_m": round(
                float(values.max()), 2
            ),
            "minimum_roughness_m": round(
                float(values.min()), 2
            )
        }


def main():
    files = sorted(DATA_FOLDER.glob("*.tif"))

    results = []

    print("\nTERRATIME 4D - TERRAIN ROUGHNESS ANALYSIS")
    print("----------------------------------------")

    if not files:
        print("No DEM files found:", DATA_FOLDER)
        return

    for file_path in files:

        try:
            result = analyze_roughness(file_path)

            if result is None:
                print("Skipped:", file_path.name)
                continue

            results.append(result)

            print("\nTile:", result["tile"])
            print(
                "Average roughness:",
                result["average_roughness_m"],
                "m"
            )

        except Exception as error:
            print("Error processing", file_path.name, ":", error)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nRoughness report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
