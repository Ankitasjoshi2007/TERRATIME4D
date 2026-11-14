from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "data/processed/environmental_comparison/six_candidate_environmental_comparison.csv"
OUT_DIR = ROOT / "results/member4_similarity_scoring"
OUTPUT = OUT_DIR / "environmental_screening_scores.csv"
REPORT = OUT_DIR / "environmental_screening_methodology.md"


def relative_index(series, higher_is_better):
    """Relative percentile rank among the six Earth candidates."""
    values = series.rank(method="average", pct=True)
    if not higher_is_better:
        values = 1 - values + (1 / len(series))
    return values * 100


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    df = pd.read_csv(INPUT)

    required = {
        "candidate",
        "mean_temperature_c",
        "mean_solar_irradiance_w_m2",
        "annual_mean_aod_55",
        "mean_water_occurrence_percent",
        "persistent_water_pixels_percent",
        "geological_record_count",
    }

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing input columns: {sorted(missing)}")

    if len(df) != 6 or df["candidate"].nunique() != 6:
        raise ValueError("Expected exactly six unique candidates.")

    metrics = [
        "mean_temperature_c",
        "mean_solar_irradiance_w_m2",
        "annual_mean_aod_55",
        "mean_water_occurrence_percent",
        "persistent_water_pixels_percent",
        "geological_record_count",
    ]

    if df[metrics].isna().any().any():
        raise ValueError(
            "Missing environmental values found. "
            "Do not silently replace missing evidence with zero."
        )

    df["solar_power_relative_index"] = relative_index(
        df["mean_solar_irradiance_w_m2"], True
    )

    df["low_aerosol_relative_index"] = relative_index(
        df["annual_mean_aod_55"], False
    )

    df["dry_site_relative_index"] = relative_index(
        df["mean_water_occurrence_percent"], False
    )

    df["water_resource_relative_index"] = relative_index(
        df["mean_water_occurrence_percent"], True
    )

    df["persistent_water_relative_index"] = relative_index(
        df["persistent_water_pixels_percent"], True
    )

    df["solar_rank"] = df["mean_solar_irradiance_w_m2"].rank(
        ascending=False, method="min"
    ).astype(int)

    df["aerosol_rank"] = df["annual_mean_aod_55"].rank(
        ascending=True, method="min"
    ).astype(int)

    df["dry_site_rank"] = df["mean_water_occurrence_percent"].rank(
        ascending=True, method="min"
    ).astype(int)

    df["water_resource_rank"] = df["mean_water_occurrence_percent"].rank(
        ascending=False, method="min"
    ).astype(int)

    columns = [
        "candidate",
        "mean_temperature_c",
        "mean_solar_irradiance_w_m2",
        "solar_power_relative_index",
        "solar_rank",
        "annual_mean_aod_55",
        "low_aerosol_relative_index",
        "aerosol_rank",
        "mean_water_occurrence_percent",
        "dry_site_relative_index",
        "dry_site_rank",
        "water_resource_relative_index",
        "water_resource_rank",
        "persistent_water_pixels_percent",
        "persistent_water_relative_index",
        "geological_record_count",
    ]

    result = df[columns].sort_values("candidate").reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    methodology = """# Member 4 — Environmental Screening

## Purpose

This module produces separate, mission-relevant environmental indicators
for the six Earth candidate locations.

## Relative index

Each indicator uses percentile ranking within the six candidates.
The result ranges from 0 to 100 and describes relative position within
this candidate set only.

## Indicator direction

- Solar power: higher irradiance ranks more favourably.
- Low aerosol: lower aerosol optical depth ranks more favourably.
- Dry-site analogue: lower surface-water occurrence ranks more favourably.
- Water-resource prospecting: higher water occurrence ranks more favourably.
- Persistent water: higher observed persistence ranks more favourably.

## Excluded from composite scoring

Temperature is retained as a measured value because no validated
planetary thermal target or acceptable operating range is supplied.

Geological record count is retained as evidence coverage only. It does
not measure mineral abundance, geological diversity, or resource value.

## Limitations

- All indices are relative to only six Earth candidates.
- Aerosol optical depth is not a dust-only measurement.
- Surface-water occurrence is a historical Earth observation product.
- NASA POWER temperature and solar data represent 2020.
- These are environmental screening indicators, not Moon/Mars similarity
  probabilities or complete mission-suitability scores.
- No weighted composite is produced until mission requirements and
  scientifically justified weights are defined.
"""

    REPORT.write_text(methodology, encoding="utf-8")

    print("\nMEMBER 4 — ENVIRONMENTAL SCREENING COMPLETE")
    print("Candidates:", len(result))
    print("\nSolar power ranking:")
    print(result.sort_values("solar_rank")[[
        "candidate", "mean_solar_irradiance_w_m2", "solar_rank"
    ]].to_string(index=False))

    print("\nDry-site ranking:")
    print(result.sort_values("dry_site_rank")[[
        "candidate", "mean_water_occurrence_percent", "dry_site_rank"
    ]].to_string(index=False))

    print("\nWater-resource ranking:")
    print(result.sort_values("water_resource_rank")[[
        "candidate", "mean_water_occurrence_percent",
        "water_resource_rank"
    ]].to_string(index=False))

    print("\nSaved:", OUTPUT)
    print("Methodology:", REPORT)


if __name__ == "__main__":
    main()
