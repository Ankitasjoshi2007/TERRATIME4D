import pandas as pd
from pathlib import Path
import shutil

main = Path("data/processed/earth_candidate_profiles/integrated_earth_candidate_profiles.csv")
summary_file = Path("data/processed/nasa_power_analysis/nasa_aerosol_annual_summary.csv")
monthly_file = Path("data/processed/environmental/nasa_power_monthly_aerosol_2020.csv")

profiles = pd.read_csv(main)
summary = pd.read_csv(summary_file)
monthly = pd.read_csv(monthly_file)

coordinates = monthly[
    ["location", "latitude", "longitude"]
].drop_duplicates()

aerosol = summary.merge(
    coordinates,
    on="location",
    validate="one_to_one"
)

result = profiles.merge(
    aerosol.drop(columns=["location", "year"]),
    on=["latitude", "longitude"],
    how="left",
    validate="one_to_one"
)

assert len(result) == len(profiles) == 6
assert result["annual_mean_aod_55"].notna().all()
assert result["annual_mean_adjusted_aod"].notna().all()

backup = main.with_name("integrated_earth_candidate_profiles_pre_aerosol.csv")
shutil.copy2(main, backup)

result.to_csv(main, index=False)

print("AEROSOL INTEGRATION COMPLETE")
print("Candidate profiles:", len(result))
print("Aerosol matches:", result["annual_mean_aod_55"].notna().sum())
print("Missing matches:", result["annual_mean_aod_55"].isna().sum())
print("\nIntegrated aerosol values:")
print(result[[
    "candidate",
    "annual_mean_aod_55",
    "maximum_month",
    "maximum_aod_55",
    "monthly_aod_std"
]].to_string(index=False))
print("\nUpdated:", main)
print("Backup:", backup)
