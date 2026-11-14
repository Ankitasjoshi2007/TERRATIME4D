from pathlib import Path
import csv
import math

BASE = Path("data/processed")

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

locations = read_csv(BASE / "global_geology_land_pilot/priority_candidate_locations.csv")
geology = read_csv(BASE / "global_geology_land_pilot/priority_candidate_records.csv")
climate = read_csv(BASE / "nasa_power_analysis/nasa_power_annual_summary.csv")
terrain = read_csv(BASE / "global_terrain/global_advanced_terrain_summary.csv")

climate_aliases = {
    "Western Australia": "Western Australia",
    "Queensland Australia": "Queensland",
    "Baja California Mexico": "Baja California",
    "Ontario Canada": "Ontario",
    "Brooks Range Alaska": "Brooks Range",
    "Scandinavia": "Scandinavia",
}

climate_index = {r["location"]: r for r in climate}
terrain_index = {r["raster_file"].lower(): r for r in terrain}

geology_index = {r["location"]: [] for r in locations}
coordinate_index = {}

for loc in locations:
    key = (
        round(float(loc["target_latitude"]), 4),
        round(float(loc["target_longitude"]), 4)
    )
    coordinate_index[key] = loc["location"]

for record in geology:
    key = (
        round(float(record["latitude"]), 4),
        round(float(record["longitude"]), 4)
    )
    candidate = coordinate_index.get(key)
    if candidate is None:
        raise ValueError(f"Unmatched geology coordinates: {key}")
    geology_index[candidate].append(record)

profiles = []

for loc in locations:
    name = loc["location"]
    lat = float(loc["target_latitude"])
    lon = float(loc["target_longitude"])

    climate_name = climate_aliases[name]
    climate_row = climate_index[climate_name]

    # DEM filenames identify the 1-degree tile containing the point.
    tile_lat = math.floor(lat)
    tile_lon = math.floor(lon)

    ns = "n" if tile_lat >= 0 else "s"
    ew = "e" if tile_lon >= 0 else "w"

    expected_tile = (
        f"copernicus_dsm_cog_30_{ns}{abs(tile_lat):02d}_00_"
        f"{ew}{abs(tile_lon):03d}_00_dem.tif"
    )

    terrain_row = terrain_index.get(expected_tile.lower())
    records = geology_index[name]

    lithologies = sorted({
        r["lithology"].strip()
        for r in records if r["lithology"].strip()
    })

    valid_ages = []
    for r in records:
        try:
            a = float(r["top_age_ma"])
            b = float(r["bottom_age_ma"])
            valid_ages.append((min(a, b), max(a, b)))
        except (ValueError, TypeError):
            pass

    row = {
        "candidate": name,
        "latitude": loc["target_latitude"],
        "longitude": loc["target_longitude"],

        "climate_year": 2020,
        "climate_months_present": climate_row["months_present"],
        "mean_temperature_c": climate_row["annual_mean_temperature_c"],
        "mean_daily_max_temperature_c": climate_row["annual_mean_daily_max_temperature_c"],
        "mean_daily_min_temperature_c": climate_row["annual_mean_daily_min_temperature_c"],
        "mean_solar_irradiance_w_m2": climate_row["annual_mean_solar_irradiance_w_m2"],

        "geological_record_count": len(records),
        "records_with_lithology": len(lithologies),
        "lithology_descriptions": " | ".join(lithologies),
        "youngest_reported_age_bound_ma": min((a for a, b in valid_ages), default=""),
        "oldest_reported_age_bound_ma": max((b for a, b in valid_ages), default=""),

        "terrain_status": "MATCHED" if terrain_row else "NOT AVAILABLE",
        "expected_terrain_tile": expected_tile,
    }

    # Preserve every terrain summary field, without inventing missing values.
    terrain_fields = [
        "elevation_min_m", "elevation_max_m", "elevation_mean_m",
        "roughness_270m_mean", "roughness_270m_p90",
        "roughness_630m_mean", "roughness_630m_p90",
        "roughness_1350m_mean", "roughness_1350m_p90",
        "hidden_slope_p30_degrees", "hidden_roughness_p70_m",
        "hidden_ruggedness_percent", "transition_hotspot_percent",
        "slope_mean_degrees", "slope_p90_degrees",
    ]

    for field in terrain_fields:
        row["terrain_" + field] = terrain_row[field] if terrain_row else ""

    profiles.append(row)

out = BASE / "earth_candidate_profiles"
write_csv(out / "integrated_earth_candidate_profiles.csv", profiles)

matched = sum(r["terrain_status"] == "MATCHED" for r in profiles)
missing = len(profiles) - matched

assert len(profiles) == 6
assert sum(int(r["geological_record_count"]) for r in profiles) == 23
assert all(int(r["climate_months_present"]) == 12 for r in profiles)
assert matched + missing == 6

print("\nINTEGRATED EARTH CANDIDATE DATASET CREATED")
print("Candidate profiles:", len(profiles))
print("Climate profiles matched:", len(climate))
print("Geological records preserved:", sum(int(r["geological_record_count"]) for r in profiles))
print("Terrain tiles matched:", matched)
print("Terrain tiles unavailable:", missing)

for r in profiles:
    print(f"{r['candidate']}: terrain={r['terrain_status']}")

print("\nVALIDATION: PASS")
print(out / "integrated_earth_candidate_profiles.csv")
