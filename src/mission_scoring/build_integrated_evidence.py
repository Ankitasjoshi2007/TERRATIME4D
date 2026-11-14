from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/member4_similarity_scoring"
OUT.mkdir(parents=True, exist_ok=True)

def load_csv(relative_path):
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)

# Member 1: Earth terrain
terrain = load_csv(
    "data/processed/combined_priority_candidate_terrain.csv"
)
terrain = terrain.rename(columns={"location": "candidate"})

# Member 2: environmental conditions
environment = load_csv(
    "data/processed/environmental_comparison/"
    "six_candidate_environmental_comparison.csv"
)
environment = environment[
    [
        "candidate",
        "mean_temperature_c",
        "mean_solar_irradiance_w_m2",
        "annual_mean_aod_55",
        "mean_water_occurrence_percent",
        "pixels_with_detected_water_percent",
        "persistent_water_pixels_percent",
        "geological_record_count",
    ]
].rename(
    columns={"geological_record_count": "environment_geological_record_count"}
)

# Member 2: aerosol variability
aerosol = load_csv(
    "data/processed/dust_aerosol_analysis/"
    "candidate_aerosol_variability.csv"
)

# Member 2: cold-climate screening
cold = load_csv(
    "data/processed/ice_climate_analysis/"
    "six_candidate_cold_climate_screening.csv"
)

# Standardise shortened candidate names in the cold-climate table.
aliases = {
    "Brooks Range": "Brooks Range Alaska",
    "Ontario": "Ontario Canada",
    "Baja California": "Baja California Mexico",
    "Queensland": "Queensland Australia",
}
cold["candidate"] = cold["candidate"].replace(aliases)
cold = cold.rename(columns={"months_analysed": "cold_months_analysed"})

# Member 2: geology/mineral evidence, joined by exact coordinates.
minerals = load_csv(
    "data/processed/mineral_lithology_analysis/"
    "candidate_mineral_lithology_screening.csv"
).rename(
    columns={"geological_records": "mineral_geological_records"}
)

# Member 2: volcanic/possible karst evidence, also joined by coordinates.
volcanic = load_csv(
    "data/processed/volcanic_karst_analysis/"
    "volcanic_karst_candidate_screening.csv"
).rename(
    columns={"geological_records": "volcanic_geological_records"}
)

# Check source uniqueness before joining.
for name, frame, keys in [
    ("terrain", terrain, ["candidate"]),
    ("environment", environment, ["candidate"]),
    ("aerosol", aerosol, ["candidate"]),
    ("cold climate", cold, ["candidate"]),
    ("minerals", minerals, ["latitude", "longitude"]),
    ("volcanic/karst", volcanic, ["latitude", "longitude"]),
]:
    if frame.duplicated(keys).any():
        raise ValueError(f"Duplicate join keys found in {name}: {keys}")

# Start with the six terrain candidates as the master candidate list.
integrated = terrain.copy()
expected_candidates = set(terrain["candidate"])

for name, frame in [
    ("environment", environment),
    ("aerosol", aerosol),
    ("cold climate", cold),
]:
    if set(frame["candidate"]) != expected_candidates:
        raise ValueError(
            f"{name} candidate names do not exactly match the terrain list.\n"
            f"Missing: {expected_candidates - set(frame['candidate'])}\n"
            f"Unexpected: {set(frame['candidate']) - expected_candidates}"
        )
    integrated = integrated.merge(
        frame, on="candidate", how="left", validate="one_to_one"
    )

# Coordinate joins: do not infer a candidate from row order.
integrated = integrated.merge(
    minerals,
    on=["latitude", "longitude"],
    how="left",
    validate="one_to_one",
    indicator="_mineral_match",
)
integrated = integrated.merge(
    volcanic,
    on=["latitude", "longitude"],
    how="left",
    validate="one_to_one",
    indicator="_volcanic_match",
)

# Explicit source-coverage flags. A matched zero remains a real zero.
integrated["terrain_evidence_present"] = True
integrated["environment_evidence_present"] = (
    integrated["mean_temperature_c"].notna()
)
integrated["aerosol_evidence_present"] = (
    integrated["annual_mean_aod"].notna()
)
integrated["cold_climate_evidence_present"] = (
    integrated["cold_months_analysed"].notna()
)
integrated["mineral_evidence_present"] = (
    integrated["_mineral_match"] == "both"
)
integrated["volcanic_karst_evidence_present"] = (
    integrated["_volcanic_match"] == "both"
)

coverage_columns = [
    "terrain_evidence_present",
    "environment_evidence_present",
    "aerosol_evidence_present",
    "cold_climate_evidence_present",
    "mineral_evidence_present",
    "volcanic_karst_evidence_present",
]
integrated["evidence_sources_present"] = integrated[
    coverage_columns
].sum(axis=1)
integrated["evidence_sources_expected"] = len(coverage_columns)

integrated = integrated.drop(
    columns=["_mineral_match", "_volcanic_match"]
)

# Final integrity checks.
if len(integrated) != 6:
    raise ValueError(f"Expected 6 candidates, got {len(integrated)}")

if integrated["candidate"].duplicated().any():
    raise ValueError("Duplicate candidates in integrated output")

if not integrated[coverage_columns].all().all():
    missing = integrated.loc[
        ~integrated[coverage_columns].all(axis=1),
        ["candidate"] + coverage_columns,
    ]
    raise ValueError(
        "One or more evidence sources failed to match:\n"
        + missing.to_string(index=False)
    )

output = OUT / "integrated_candidate_evidence.csv"
integrated.to_csv(output, index=False)

print("\nINTEGRATED EVIDENCE BUILD: PASSED")
print("Candidates:", len(integrated))
print("Columns:", len(integrated.columns))
print("\nEvidence coverage:")
print(
    integrated[
        ["candidate", "evidence_sources_present",
         "evidence_sources_expected"]
    ].to_string(index=False)
)
print("\nOutput:", output.relative_to(ROOT))
print("\nIntegrated columns:")
print(integrated.columns.tolist())
