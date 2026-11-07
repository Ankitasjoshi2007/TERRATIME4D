
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_sample_plan.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_distribution.png"
)


def assign_longitude_band(longitude):
    if -180 <= longitude < -120:
        return "120W to 180W"
    elif -120 <= longitude < -60:
        return "60W to 120W"
    elif -60 <= longitude < 0:
        return "0 to 60W"
    elif 0 <= longitude < 60:
        return "0 to 60E"
    elif 60 <= longitude < 120:
        return "60E to 120E"
    elif 120 <= longitude <= 180:
        return "120E to 180E"
    return "Outside range"


def main():
    print("\nTERRATIME 4D - GLOBAL DEM DISTRIBUTION CHART")
    print("--------------------------------------------")

    sample = pd.read_csv(INPUT_FILE)

    if "latitude_band" not in sample.columns:
        raise ValueError("latitude_band column is missing.")

    sample["longitude_band"] = sample[
        "tile_longitude"
    ].apply(assign_longitude_band)

    distribution = pd.crosstab(
        sample["latitude_band"],
        sample["longitude_band"]
    )

    ax = distribution.plot(
        kind="bar",
        stacked=True,
        figsize=(12, 7)
    )

    ax.set_title("Global Copernicus DEM Sample Distribution")
    ax.set_xlabel("Latitude Band")
    ax.set_ylabel("Number of DEM Tiles")
    ax.legend(
        title="Longitude Band",
        bbox_to_anchor=(1.02, 1)
    )

    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(OUTPUT_FILE, dpi=300)
    plt.close()

    print("Chart saved successfully:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
