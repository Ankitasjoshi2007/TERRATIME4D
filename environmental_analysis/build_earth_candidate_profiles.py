from pathlib import Path
import csv

BASE = Path("data/processed")

LOCATIONS_FILE = BASE / "global_geology_land_pilot/priority_candidate_locations.csv"
GEOLOGY_FILE = BASE / "global_geology_land_pilot/priority_candidate_records.csv"
CLIMATE_FILE = BASE / "nasa_power_analysis/nasa_power_annual_summary.csv"

OUT = BASE / "earth_candidate_profiles"
OUT.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

locations = read_csv(LOCATIONS_FILE)
geology = read_csv(GEOLOGY_FILE)
climate = read_csv(CLIMATE_FILE)

# Match candidate names to the NASA POWER location labels.
climate_aliases = {
    "Western Australia": "Western Australia",
    "Queensland Australia": "Queensland",
    "Baja California Mexico": "Baja California",
    "Ontario Canada": "Ontario",
    "Brooks Range Alaska": "Brooks Range",
    "Scandinavia": "Scandinavia",
}

# Index candidates by their exact target coordinates.
candidate_by_coords = {}
for loc in locations:
    key = (
        round(float(loc["target_latitude"]), 4),
        round(float(loc["target_longitude"]), 4),
    )
    if key in candidate_by_coords:
        raise ValueError(f"Duplicate candidate coordinates: {key}")
    candidate_by_coords[key] = loc["location"]

# Attach each geological record to its exact candidate coordinates.
geology_by_candidate = {loc["location"]: [] for loc in locations}

for record in geology:
    key = (
        round(float(record["latitude"]), 4),
        round(float(record["longitude"]), 4),
    )
    candidate = candidate_by_coords.get(key)

    if candidate is None:
        raise ValueError(f"Geology coordinates do not match a candidate: {key}")

    geology_by_candidate[candidate].append(record)

climate_by_location = {row["location"]: row for row in climate}

profile_rows = []
detail_rows = []

for loc in locations:
    candidate = loc["location"]
    climate_name = climate_aliases[candidate]

    if climate_name not in climate_by_location:
        raise ValueError(f"Missing climate summary for {candidate}")

    climate_row = climate_by_location[climate_name]
    records = geology_by_candidate[candidate]

    lithologies = sorted({
        r["lithology"].strip()
        for r in records if r["lithology"].strip()
    })

    names = sorted({
        r["name"].strip()
        for r in records if r["name"].strip()
    })

    valid_ages = []
    for r in records:
        try:
            a = float(r["top_age_ma"])
            b = float(r["bottom_age_ma"])
            valid_ages.append((min(a, b), max(a, b)))
        except (ValueError, TypeError):
            continue

    younger_bound = min((a for a, b in valid_ages), default="")
    older_bound = max((b for a, b in valid_ages), default="")

    profile_rows.append({
        "candidate": candidate,
        "latitude": loc["target_latitude"],
        "longitude": loc["target_longitude"],
        "climate_data_year": 2020,
        "climate_months_present": climate_row["months_present"],
        "mean_temperature_c": climate_row["annual_mean_temperature_c"],
        "mean_daily_max_temperature_c": climate_row["annual_mean_daily_max_temperature_c"],
        "mean_daily_min_temperature_c": climate_row["annual_mean_daily_min_temperature_c"],
        "mean_solar_irradiance_w_m2": climate_row["annual_mean_solar_irradiance_w_m2"],
        "geological_record_count": len(records),
        "records_with_lithology": len(lithologies),
        "distinct_lithology_descriptions": " | ".join(lithologies),
        "geological_unit_names": " | ".join(names),
        "youngest_reported_age_bound_ma": younger_bound,
        "oldest_reported_age_bound_ma": older_bound,
    })

    for r in records:
        try:
            a = float(r["top_age_ma"])
            b = float(r["bottom_age_ma"])
            younger, older = min(a, b), max(a, b)
        except (ValueError, TypeError):
            younger, older = "", ""

        detail_rows.append({
            "candidate": candidate,
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "geological_unit_name": r["name"],
            "lithology": r["lithology"],
            "top_age_ma_as_reported": r["top_age_ma"],
            "bottom_age_ma_as_reported": r["bottom_age_ma"],
            "younger_age_bound_ma": younger,
            "older_age_bound_ma": older,
        })

profile_fields = list(profile_rows[0].keys())
detail_fields = list(detail_rows[0].keys())

def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

write_csv(OUT / "earth_candidate_environmental_geological_profiles.csv",
          profile_rows, profile_fields)

write_csv(OUT / "earth_candidate_geology_details.csv",
          detail_rows, detail_fields)

# Integration checks
assert len(profile_rows) == 6
assert len({r["candidate"] for r in profile_rows}) == 6
assert len(detail_rows) == len(geology) == 23
assert all(int(r["climate_months_present"]) == 12 for r in profile_rows)
assert sum(int(r["geological_record_count"]) for r in profile_rows) == 23

print("\nEARTH CANDIDATE PROFILE INTEGRATION COMPLETE")
print("Candidate profiles:", len(profile_rows))
print("Geological detail records:", len(detail_rows))
print("Climate summaries matched:", len(profile_rows))
print("\nGeology records per candidate:")
for row in profile_rows:
    print(f"  {row['candidate']}: {row['geological_record_count']}")

print("\nVALIDATION: PASS")
print("Outputs:")
print(OUT / "earth_candidate_environmental_geological_profiles.csv")
print(OUT / "earth_candidate_geology_details.csv")
