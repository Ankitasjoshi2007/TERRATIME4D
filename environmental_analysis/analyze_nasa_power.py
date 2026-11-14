import csv
from pathlib import Path
from collections import defaultdict

BASE = Path("data/processed/environmental")
OUT = Path("data/processed/nasa_power_analysis")
OUT.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

temperature = read_csv(BASE / "nasa_power_monthly_temperature_2020.csv")
solar = read_csv(BASE / "nasa_power_monthly_solar_2020.csv")

solar_lookup = {
    (r["location"], int(r["year_month"][4:6])): float(r["solar_irradiance_w_m2"])
    for r in solar
}

combined = []
for r in temperature:
    month = int(r["month"])
    key = (r["location"], month)

    if key not in solar_lookup:
        continue

    combined.append({
        "location": r["location"],
        "latitude": r["latitude"],
        "longitude": r["longitude"],
        "year": r["year"],
        "month": month,
        "mean_temperature_c": float(r["mean_temperature_c"]),
        "mean_daily_max_temperature_c": float(r["mean_daily_max_temperature_c"]),
        "mean_daily_min_temperature_c": float(r["mean_daily_min_temperature_c"]),
        "solar_irradiance_w_m2": solar_lookup[key]
    })

fields = [
    "location", "latitude", "longitude", "year", "month",
    "mean_temperature_c", "mean_daily_max_temperature_c",
    "mean_daily_min_temperature_c", "solar_irradiance_w_m2"
]
write_csv(OUT / "nasa_power_monthly_combined.csv", combined, fields)

# Meteorological seasons
seasons = {
    "DJF": [12, 1, 2],
    "MAM": [3, 4, 5],
    "JJA": [6, 7, 8],
    "SON": [9, 10, 11]
}

grouped = defaultdict(list)
for r in combined:
    for season, months in seasons.items():
        if r["month"] in months:
            grouped[(r["location"], season)].append(r)
            break

seasonal_rows = []
for (location, season), rows in sorted(grouped.items()):
    n = len(rows)
    seasonal_rows.append({
        "location": location,
        "season": season,
        "months_present": n,
        "mean_temperature_c": sum(r["mean_temperature_c"] for r in rows) / n,
        "mean_daily_max_temperature_c": sum(r["mean_daily_max_temperature_c"] for r in rows) / n,
        "mean_daily_min_temperature_c": sum(r["mean_daily_min_temperature_c"] for r in rows) / n,
        "mean_solar_irradiance_w_m2": sum(r["solar_irradiance_w_m2"] for r in rows) / n
    })

write_csv(
    OUT / "nasa_power_seasonal_summary.csv",
    seasonal_rows,
    [
        "location", "season", "months_present",
        "mean_temperature_c", "mean_daily_max_temperature_c",
        "mean_daily_min_temperature_c", "mean_solar_irradiance_w_m2"
    ]
)

# Annual averages across the 12 monthly observations
annual_groups = defaultdict(list)
for r in combined:
    annual_groups[r["location"]].append(r)

annual_rows = []
for location, rows in sorted(annual_groups.items()):
    n = len(rows)
    annual_rows.append({
        "location": location,
        "months_present": n,
        "annual_mean_temperature_c": sum(r["mean_temperature_c"] for r in rows) / n,
        "annual_mean_daily_max_temperature_c": sum(r["mean_daily_max_temperature_c"] for r in rows) / n,
        "annual_mean_daily_min_temperature_c": sum(r["mean_daily_min_temperature_c"] for r in rows) / n,
        "annual_mean_solar_irradiance_w_m2": sum(r["solar_irradiance_w_m2"] for r in rows) / n
    })

write_csv(
    OUT / "nasa_power_annual_summary.csv",
    annual_rows,
    [
        "location", "months_present", "annual_mean_temperature_c",
        "annual_mean_daily_max_temperature_c",
        "annual_mean_daily_min_temperature_c",
        "annual_mean_solar_irradiance_w_m2"
    ]
)

# Input and join quality checks
temp_keys = {(r["location"], int(r["month"])) for r in temperature}
solar_keys = {
    (r["location"], int(r["year_month"][4:6]))
    for r in solar
}
quality = [{
    "temperature_records": len(temperature),
    "solar_records": len(solar),
    "combined_records": len(combined),
    "temperature_duplicate_keys": len(temperature) - len(temp_keys),
    "solar_duplicate_keys": len(solar) - len(solar_keys),
    "unmatched_temperature_months": len(temp_keys - solar_keys),
    "unmatched_solar_months": len(solar_keys - temp_keys),
    "locations": len(annual_rows),
    "locations_with_12_months": sum(r["months_present"] == 12 for r in annual_rows)
}]

write_csv(
    OUT / "nasa_power_data_quality.csv",
    quality,
    list(quality[0].keys())
)

print("\nNASA POWER ANALYSIS COMPLETE")
print("Temperature records:", len(temperature))
print("Solar records:", len(solar))
print("Combined monthly records:", len(combined))
print("Locations:", len(annual_rows))
print("\nAnnual summaries:")
for r in annual_rows:
    print(
        r["location"],
        "| Mean temperature:", round(r["annual_mean_temperature_c"], 2), "C",
        "| Mean solar:", round(r["annual_mean_solar_irradiance_w_m2"], 2), "W/m2"
    )

print("\nOutputs:")
for p in sorted(OUT.glob("*.csv")):
    print("CREATED:", p.name)
