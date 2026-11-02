from pathlib import Path
import numpy as np
import pandas as pd
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "dem_quality_report.csv"


def inspect_tile(file_path):
    with rasterio.open(file_path) as dataset:
        elevation = dataset.read(1, masked=True)
        values = elevation.compressed()
        values = values[np.isfinite(values)]

        if len(values) == 0:
            return {
                "file": file_path.name,
                "status": "NO VALID DATA"
            }

        return {
            "file": file_path.name,
            "valid_pixels": len(values),
            "zero_pixels": int(np.count_nonzero(values == 0)),
            "zero_percent": round(
                100 * np.count_nonzero(values == 0) / len(values), 2
            ),
            "minimum_m": round(float(values.min()), 2),
            "maximum_m": round(float(values.max()), 2),
            "average_m": round(float(values.mean()), 2),
            "status": "CHECKED"
        }


def main():
    files = sorted(DATA_FOLDER.glob("*.tif"))
    results = []

    print("\nTERRATIME 4D - FULL TILE QUALITY CHECK")
    print("--------------------------------------")

    for file_path in files:
        result = inspect_tile(file_path)
        results.append(result)

        print("\n", file_path.name)
        for key, value in result.items():
            if key != "file":
                print(f"{key}: {value}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)

    print("\nQuality report saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()