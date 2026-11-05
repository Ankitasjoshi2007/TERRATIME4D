from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "processed" / "global_dem_land_only_sample.csv"

df = pd.read_csv(INPUT_FILE)

print("\nTERRATIME 4D - LAND SAMPLE INSPECTION")
print("-------------------------------------")

print("Total selected tiles:", len(df))
print("Unique latitude bands:", df["latitude_band"].nunique())
print("Unique longitude bands:", df["longitude_band"].nunique())

print("\nTiles by latitude and longitude:")
print(
    pd.crosstab(
        df["latitude_band"],
        df["longitude_band"]
    )
)

print("\nLand percentage statistics:")
print(df["land_percentage"].describe())

print("\nDownload status:")
print(df["download_status"].value_counts())

print("\nSaved file:")
print(INPUT_FILE)