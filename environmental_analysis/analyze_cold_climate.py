from pathlib import Path
import pandas as pd

source = Path(
    "data/processed/nasa_power_analysis/"
    "nasa_power_monthly_combined.csv"
)

out = Path("data/processed/ice_climate_analysis")
out.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source)

required = [
    "location", "year", "month",
    "mean_temperature_c",
    "mean_daily_min_temperature_c",
    "mean_daily_max_temperature_c"
]

missing = set(required) - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

if df["location"].nunique() != 6:
    raise ValueError("Expected six candidate locations.")

rows = []

for location, group in df.groupby("location"):
    group = group.sort_values("month")

    if len(group) != 12 or group["month"].nunique() != 12:
        raise ValueError(f"Incomplete monthly data: {location}")

    rows.append({
        "candidate": location,
        "months_with_mean_temp_at_or_below_0C":
            int((group["mean_temperature_c"] <= 0).sum()),
        "months_with_mean_daily_min_at_or_below_0C":
            int((group["mean_daily_min_temperature_c"] <= 0).sum()),
        "months_with_mean_daily_max_at_or_below_0C":
            int((group["mean_daily_max_temperature_c"] <= 0).sum()),
        "annual_mean_temperature_c":
            group["mean_temperature_c"].mean(),
        "coldest_month": int(
            group.loc[group["mean_temperature_c"].idxmin(), "month"]
        ),
        "coldest_month_mean_temperature_c":
            group["mean_temperature_c"].min(),
        "lowest_monthly_mean_daily_min_c":
            group["mean_daily_min_temperature_c"].min(),
        "months_analysed": len(group)
    })

result = pd.DataFrame(rows).sort_values(
    "months_with_mean_daily_min_at_or_below_0C",
    ascending=False
)

target = out / "six_candidate_cold_climate_screening.csv"
result.to_csv(target, index=False)

report = [
    "# TERRATIME4D — Cold-Climate Screening",
    "",
    "Source: NASA POWER monthly data for 2020.",
    "",
    "This is a temperature-based cold-climate proxy, NOT a glacier inventory.",
    "Monthly averages cannot establish daily frost frequency, snow persistence,",
    "ice thickness, glacier presence or glacier mass balance.",
    "",
    "## Candidate results",
    "",
    result.to_string(index=False),
    "",
    "## Interpretation",
    "- Months with mean daily minimum at or below 0°C indicate potential",
    "  seasonal freezing conditions.",
    "- Months with mean daily maximum at or below 0°C indicate colder",
    "  conditions throughout the average day.",
    "- These indicators must not be interpreted as confirmed ice coverage."
]

(out / "cold_climate_screening_report.md").write_text(
    "\n".join(report), encoding="utf-8"
)

print("\nCOLD-CLIMATE SCREENING COMPLETE")
print(result.to_string(index=False))
print("\nSaved:", target)
print("Saved:", out / "cold_climate_screening_report.md")
