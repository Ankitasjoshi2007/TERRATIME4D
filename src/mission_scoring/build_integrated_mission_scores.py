from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/member4_similarity_scoring"
OUT.mkdir(parents=True, exist_ok=True)

evidence = pd.read_csv(OUT / "integrated_candidate_evidence.csv")
terrain = pd.read_csv(OUT / "terrain_similarity_scores.csv")

if evidence["candidate"].duplicated().any():
    raise ValueError("Duplicate candidates in integrated evidence")

candidates = evidence["candidate"].tolist()

def relative_index(series, higher_is_better=True):
    values = pd.to_numeric(series, errors="coerce")
    if values.isna().any():
        raise ValueError(f"Missing values in scoring feature: {series.name}")
    low, high = values.min(), values.max()
    if high == low:
        return pd.Series(50.0, index=values.index)
    result = (values - low) / (high - low) * 100
    return result if higher_is_better else 100 - result

# Terrain similarity: convert the existing planetary-specific rank
# into a transparent relative index. This is slope-based only.
terrain_indices = {}
for planet in ["Moon", "Mars"]:
    subset = terrain[terrain["planet"] == planet].copy()
    if set(subset["candidate"]) != set(candidates):
        raise ValueError(f"Terrain scores do not cover all candidates for {planet}")
    count = len(subset)
    subset["terrain_index"] = (
        100 * (1 - (subset["rank_within_planet"] - 1) / (count - 1))
    )
    terrain_indices[planet] = subset.set_index("candidate")["terrain_index"]

# Environmental components, each scaled across the six candidates.
features = pd.DataFrame(index=evidence.index)
features["solar"] = relative_index(
    evidence["mean_solar_irradiance_w_m2"], True
)
features["dry_site"] = relative_index(
    evidence["mean_water_occurrence_percent"], False
)
features["water"] = relative_index(
    evidence["mean_water_occurrence_percent"], True
)
features["persistent_water"] = relative_index(
    evidence["persistent_water_pixels_percent"], True
)
features["cold_months"] = relative_index(
    evidence["months_with_mean_temp_at_or_below_0C"], True
)
features["coldest_month"] = relative_index(
    evidence["coldest_month_mean_temperature_c"], False
)
features["aerosol_mean"] = relative_index(
    evidence["annual_mean_aod"], True
)
features["aerosol_variability"] = relative_index(
    evidence["aod_range"], True
)
features["high_loading_months"] = relative_index(
    evidence["high_loading_months"], True
)

# Geological indicators are normalised by their respective record counts.
# They indicate recorded evidence, not abundance or confirmed resources.
mineral_records = evidence["mineral_geological_records"].replace(0, pd.NA)
volcanic_records = evidence["volcanic_geological_records"].replace(0, pd.NA)

features["volcanic_evidence_rate"] = relative_index(
    evidence["volcanic_rock_mentions"] / volcanic_records, True
)
features["karst_evidence_rate"] = relative_index(
    evidence["possible_karst_host_rock_mentions"] / volcanic_records, True
)

profiles = [
    {
        "name": "Lunar rover mobility",
        "planet": "Moon",
        "type": "Planetary terrain screening",
        "weights": {"terrain": 0.80, "solar": 0.20},
    },
    {
        "name": "Lunar polar operations",
        "planet": "Moon",
        "type": "Terrestrial polar-environment analogue",
        "weights": {
            "terrain": 0.25, "solar": 0.25,
            "cold_months": 0.25, "water": 0.25,
        },
    },
    {
        "name": "Mars rover mobility",
        "planet": "Mars",
        "type": "Planetary terrain and dry-site screening",
        "weights": {
            "terrain": 0.65, "dry_site": 0.15,
            "solar": 0.10, "aerosol_mean": 0.10,
        },
    },
    {
        "name": "Lunar resource prospecting",
        "planet": "Moon",
        "type": "Terrestrial water-indicator screening",
        "weights": {
            "terrain": 0.20, "water": 0.60,
            "persistent_water": 0.20,
        },
    },
    {
        "name": "Mars dust-process analogue",
        "planet": "Mars",
        "type": "Earth aerosol-process analogue",
        "weights": {
            "aerosol_mean": 0.40,
            "aerosol_variability": 0.35,
            "high_loading_months": 0.25,
        },
    },
    {
        "name": "Volcanic and cave analogue reconnaissance",
        "planet": "Not planet-specific",
        "type": "Earth geological analogue screening",
        "weights": {
            "volcanic_evidence_rate": 0.50,
            "karst_evidence_rate": 0.50,
        },
    },
    {
        "name": "Cold-region operations analogue",
        "planet": "Not planet-specific",
        "type": "Earth cold-environment analogue screening",
        "weights": {"cold_months": 0.50, "coldest_month": 0.50},
    },
]

rows = []

for profile in profiles:
    weights = profile["weights"]
    component_values = {}

    if "terrain" in weights:
        component_values["terrain"] = terrain_indices[
            profile["planet"]
        ].reindex(candidates).reset_index(drop=True)

    for feature in weights:
        if feature != "terrain":
            component_values[feature] = features[feature].reset_index(drop=True)

    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError(f"Weights do not sum to 1 for {profile['name']}")

    for i, candidate in enumerate(candidates):
        contributions = {
            key: float(component_values[key].iloc[i] * weight)
            for key, weight in weights.items()
        }
        score = sum(contributions.values())

        rows.append({
            "mission_profile": profile["name"],
            "target_planet": profile["planet"],
            "profile_type": profile["type"],
            "candidate": candidate,
            "screening_index_0_100": score,
            **{
                f"{key}_index": float(component_values[key].iloc[i])
                for key in weights
            },
            **{
                f"{key}_contribution": value
                for key, value in contributions.items()
            },
            "evidence_sources_present": int(
                evidence.loc[i, "evidence_sources_present"]
            ),
            "evidence_sources_expected": int(
                evidence.loc[i, "evidence_sources_expected"]
            ),
        })

result = pd.DataFrame(rows)
result["mission_rank"] = result.groupby(
    "mission_profile"
)["screening_index_0_100"].rank(
    ascending=False, method="min"
).astype(int)

result = result.sort_values(
    ["mission_profile", "mission_rank", "candidate"]
).reset_index(drop=True)

# Validate output completeness and arithmetic.
expected_rows = len(profiles) * len(candidates)
if len(result) != expected_rows:
    raise ValueError(f"Expected {expected_rows} rows, got {len(result)}")

# Validate only fields that must exist for every scored candidate.
required_columns = [
    "mission_profile", "candidate", "screening_index_0_100", "mission_rank",
    "evidence_sources_present", "evidence_sources_expected",
]
if result[required_columns].isna().any().any():
    raise ValueError("Missing required scoring result fields")

# Component columns unused by a particular profile are intentionally blank.
for profile in profiles:
    group = result[result["mission_profile"] == profile["name"]]
    for component in profile["weights"]:
        column = f"{component}_contribution"
        if group[column].isna().any():
            raise ValueError(
                f"Missing active component {component} in {profile['name']}"
            )

for profile_name, group in result.groupby("mission_profile"):
    if len(group) != len(candidates):
        raise ValueError(f"Incomplete candidate ranking: {profile_name}")
    if set(group["candidate"]) != set(candidates):
        raise ValueError(f"Candidate mismatch: {profile_name}")

contribution_columns = [
    column for column in result.columns
    if column.endswith("_contribution")
]
reconstructed = result[contribution_columns].sum(axis=1)

if not (reconstructed - result["screening_index_0_100"]).abs().lt(1e-8).all():
    raise ValueError("Weighted contributions do not reproduce scores")

output = OUT / "integrated_mission_scores.csv"
result.to_csv(output, index=False)

print("\nINTEGRATED MISSION SCORING: PASSED")
print("Candidates:", len(candidates))
print("Mission profiles:", len(profiles))
print("Total scores:", len(result))
print("Validation: complete candidate coverage, no missing scores,")
print("             weights sum to 1, contributions reproduce totals.")
print("\nRankings:")
for name, group in result.groupby("mission_profile", sort=False):
    print(f"\n{name}")
    print(group[
        ["mission_rank", "candidate", "screening_index_0_100"]
    ].to_string(index=False))

print("\nOutput:", output.relative_to(ROOT))
