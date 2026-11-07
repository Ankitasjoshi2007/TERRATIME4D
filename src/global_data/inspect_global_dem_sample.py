
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_dem_sample_plan.csv"
)


def longitude_band(longitude):
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
    print("\nTERRATIME 4D - GLOBAL SAMPLE DISTRIBUTION")
    print("-----------------------------------------")

    sample = pd.read_csv(INPUT_FILE)

    sample["longitude_band"] = sample[
        "tile_longitude"
    ].apply(longitude_band)

    print("Total sample tiles:", len(sample))

    print("\nTiles by latitude band:")
    print(sample["latitude_band"].value_counts().to_string())

    print("\nTiles by longitude band:")
    print(sample["longitude_band"].value_counts().to_string())

    print("\nLatitude-longitude distribution:")
    distribution = pd.crosstab(
        sample["latitude_band"],
        sample["longitude_band"]
    )
    print(distribution.to_string())

    print("\nDownload status:")
    print(sample["download_status"].value_counts().to_string())


if __name__ == "__main__":
    main()
