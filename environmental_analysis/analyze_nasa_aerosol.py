import pandas as pd
from pathlib import Path

source = Path("data/processed/environmental/nasa_power_monthly_aerosol_2020.csv")
out = Path("data/processed/nasa_power_analysis")
out.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source)

required = ["location", "month", "aod_55", "aod_55_adjusted"]
assert all(c in df.columns for c in required)
assert len(df) == 72
assert df["location"].nunique() == 6
assert not df[["aod_55", "aod_55_adjusted"]].isna().any().any()

rows = []

for location, group in df.groupby("location"):
    group = group.sort_values("month")
    peak = group.loc[group["aod_55"].idxmax()]
    low = group.loc[group["aod_55"].idxmin()]

    rows.append({
        "location": location,
        "year": 2020,
        "annual_mean_aod_55": group["aod_55"].mean(),
        "annual_mean_adjusted_aod": group["aod_55_adjusted"].mean(),
        "maximum_month": int(peak["month"]),
        "maximum_aod_55": peak["aod_55"],
        "minimum_month": int(low["month"]),
        "minimum_aod_55": low["aod_55"],
        "monthly_aod_std": group["aod_55"].std(),
        "monthly_aod_range": group["aod_55"].max() - group["aod_55"].min(),
    })

summary = pd.DataFrame(rows).sort_values(
    "annual_mean_aod_55", ascending=False
)

summary.to_csv(out / "nasa_aerosol_annual_summary.csv", index=False)

quality = pd.DataFrame([{
    "records": len(df),
    "locations": df["location"].nunique(),
    "months_per_location": 12,
    "missing_aod_55": int(df["aod_55"].isna().sum()),
    "missing_adjusted_aod": int(df["aod_55_adjusted"].isna().sum()),
    "duplicate_location_months": int(
        df.duplicated(["location", "month"]).sum()
    ),
    "source": "NASA POWER CERES SYN1deg",
    "year": 2020,
}])

quality.to_csv(out / "nasa_aerosol_data_quality.csv", index=False)

print("AEROSOL ANALYSIS COMPLETE")
print("\nAnnual candidate comparison:")
print(summary.round(4).to_string(index=False))
print("\nValidation:")
print(quality.to_string(index=False))
print("\nSaved:")
print(out / "nasa_aerosol_annual_summary.csv")
print(out / "nasa_aerosol_data_quality.csv")
