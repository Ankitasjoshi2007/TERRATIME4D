from pathlib import Path
import rasterio
import pandas as pd

DATA_FOLDER = Path("data/raw/earth")
OUTPUT_FILE = Path("data/processed/srtm_elevation_summary.csv")


def inspect_elevation_files():
    hgt_files = sorted(
        file for file in DATA_FOLDER.rglob("*.hgt")
        if file.is_file()
    )

    results = []

    for file_path in hgt_files:
        with rasterio.open(file_path) as dataset:
            elevation = dataset.read(1)

            results.append({
                "file": file_path.name,
                "rows": dataset.height,
                "columns": dataset.width,
                "coordinate_system": str(dataset.crs),
                "minimum_elevation_m": int(elevation.min()),
                "maximum_elevation_m": int(elevation.max()),
                "average_elevation_m": round(
                    float(elevation.mean()), 2
                )
            })

            print("Processed:", file_path.name)

    if results:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        print("\nSummary saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    inspect_elevation_files()