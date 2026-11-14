from pathlib import Path
import pandas as pd
import shutil
from datetime import datetime

profile_path = Path(
    "data/processed/earth_candidate_profiles/"
    "integrated_earth_candidate_profiles.csv"
)

water_path = Path(
    "data/processed/environmental/"
    "jrc_surface_water_occurrence_2024.csv"
)

output_path = Path(
    "data/processed/earth_candidate_profiles/"
    "integrated_earth_candidate_profiles_complete.csv"
)

if not profile_path.exists():
    raise FileNotFoundError(profile_path)

if not water_path.exists():
    raise FileNotFoundError(water_path)

profiles = pd.read_csv(profile_path)
water = pd.read_csv(water_path)

required_profile = {"latitude", "longitude", "candidate"}
required_water = {
    "latitude", "longitude",
    "mean_water_occurrence_percent",
    "pixels_with_detected_water_percent",
    "persistent_water_pixels_percent"
}

if not required_profile.issubset(profiles.columns):
    raise ValueError("Integrated profile is missing required columns.")

if not required_water.issubset(water.columns):
    raise ValueError("Surface-water dataset is missing required columns.")

if profiles.duplicated(["latitude", "longitude"]).any():
    raise ValueError("Duplicate candidate coordinates in profiles.")

if water.duplicated(["latitude", "longitude"]).any():
    raise ValueError("Duplicate candidate coordinates in water data.")

water_columns = [
    "latitude", "longitude",
    "valid_pixels",
    "mean_water_occurrence_percent",
    "median_water_occurrence_percent",
    "pixels_with_detected_water_percent",
    "persistent_water_pixels_percent",
    "source_period"
]

merged = profiles.merge(
    water[water_columns],
    on=["latitude", "longitude"],
    how="left",
    validate="one_to_one",
    indicator=True
)

matched = (merged["_merge"] == "both").sum()

if matched != len(profiles):
    missing = merged.loc[
        merged["_merge"] != "both", "candidate"
    ].tolist()
    raise RuntimeError(f"Water data missing for: {missing}")

merged.drop(columns="_merge", inplace=True)

merged["surface_water_data_status"] = "matched"

if merged.isna().sum().sum() > 0:
    print("Note: existing source datasets contain missing values.")

merged.to_csv(output_path, index=False)

print("\nINTEGRATED ENVIRONMENTAL DATASET COMPLETE")
print("Candidate locations:", len(merged))
print("Surface-water matches:", matched)
print("Columns:", len(merged.columns))
print("Output:", output_path)

print("\nSURFACE WATER COMPARISON")
print(
    merged[[
        "candidate",
        "mean_water_occurrence_percent",
        "pixels_with_detected_water_percent",
        "persistent_water_pixels_percent"
    ]].to_string(index=False)
)
