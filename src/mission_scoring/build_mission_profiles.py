from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

TERRAIN_FILE = (
    ROOT / "results/member4_similarity_scoring/"
    "terrain_similarity_scores.csv"
)
ENV_FILE = (
    ROOT / "results/member4_similarity_scoring/"
    "environmental_screening_scores.csv"
)

OUT_DIR = ROOT / "results/member4_similarity_scoring"
OUTPUT = OUT_DIR / "mission_specific_scores.csv"
REPORT = OUT_DIR / "mission_profile_methodology.md"


# Initial transparent weights.
# These are screening assumptions, not validated mission requirements.
PROFILES = {
    "Lunar rover mobility": {
        "planet": "Moon",
        "weights": {
            "terrain": 0.80,
            "solar": 0.20,
        },
    },
    "Lunar polar operations": {
        "planet": "Moon",
        "weights": {
            "terrain": 0.35,
            "solar": 0.35,
            "water": 0.30,
        },
    },
    "Mars rover mobility": {
        "planet": "Mars",
        "weights": {
            "terrain": 0.75,
            "dry": 0.15,
            "solar": 0.10,
        },
    },
    "Lunar resource prospecting": {
        "planet": "Moon",
        "weights": {
            "terrain": 0.20,
            "water": 0.60,
            "persistent_water": 0.20,
        },
    },
}


def main():
    if not TERRAIN_FILE.exists():
        raise FileNotFoundError(TERRAIN_FILE)

    if not ENV_FILE.exists():
        raise FileNotFoundError(ENV_FILE)

    terrain = pd.read_csv(TERRAIN_FILE)
    environment = pd.read_csv(ENV_FILE)

    terrain_required = {
        "candidate",
        "planet",
        "rank_within_planet",
    }

    environment_required = {
        "candidate",
        "solar_power_relative_index",
        "dry_site_relative_index",
        "water_resource_relative_index",
        "persistent_water_relative_index",
        "geological_record_count",
    }

    if not terrain_required.issubset(terrain.columns):
        raise ValueError(
            "Terrain file is missing required columns: "
            f"{sorted(terrain_required - set(terrain.columns))}"
        )

    if not environment_required.issubset(environment.columns):
        raise ValueError(
            "Environmental file is missing required columns: "
            f"{sorted(environment_required - set(environment.columns))}"
        )

    if environment["candidate"].nunique() != 6:
        raise ValueError("Expected six unique environmental candidates.")

    if terrain.duplicated(["candidate", "planet"]).any():
        raise ValueError("Duplicate candidate/planet terrain records found.")

    # Convert ordinal terrain rankings into a relative 0–100 index.
    # This represents rank position, not the magnitude of physical similarity.
    terrain["terrain_rank_relative_index"] = (
        100 * (
            1 - (
                (terrain["rank_within_planet"] - 1) /
                (terrain.groupby("planet")["candidate"].transform("count") - 1)
            )
        )
    )

    combined = terrain.merge(
        environment,
        on="candidate",
        how="inner",
        validate="many_to_one",
    )

    if len(combined) != 12:
        raise ValueError(
            f"Expected 12 terrain/environment matches; got {len(combined)}."
        )

    if combined["candidate"].nunique() != 6:
        raise ValueError("Not all six candidates were matched.")

    output_rows = []

    for profile_name, profile in PROFILES.items():
        target_planet = profile["planet"]
        weights = profile["weights"]

        subset = combined[
            combined["planet"].str.lower() == target_planet.lower()
        ].copy()

        if len(subset) != 6:
            raise ValueError(
                f"{profile_name}: expected six {target_planet} candidates."
            )

        subset["mission_profile"] = profile_name
        subset["target_planet"] = target_planet

        subset["terrain_contribution"] = (
            subset["terrain_rank_relative_index"] *
            weights.get("terrain", 0)
        )

        subset["solar_contribution"] = (
            subset["solar_power_relative_index"] *
            weights.get("solar", 0)
        )

        subset["dry_site_contribution"] = (
            subset["dry_site_relative_index"] *
            weights.get("dry", 0)
        )

        subset["water_resource_contribution"] = (
            subset["water_resource_relative_index"] *
            weights.get("water", 0)
        )

        subset["persistent_water_contribution"] = (
            subset["persistent_water_relative_index"] *
            weights.get("persistent_water", 0)
        )

        contribution_columns = [
            "terrain_contribution",
            "solar_contribution",
            "dry_site_contribution",
            "water_resource_contribution",
            "persistent_water_contribution",
        ]

        subset["mission_screening_score"] = (
            subset[contribution_columns].sum(axis=1)
        )

        subset["mission_rank"] = (
            subset["mission_screening_score"]
            .rank(method="min", ascending=False)
            .astype(int)
        )

        # Keep geology as evidence coverage, not as a resource score.
        subset["geological_record_count"] = (
            subset["geological_record_count"].astype(int)
        )

        output_rows.append(subset)

    result = pd.concat(output_rows, ignore_index=True)

    columns = [
        "mission_profile",
        "target_planet",
        "candidate",
        "mission_screening_score",
        "mission_rank",
        "terrain_rank_relative_index",
        "terrain_contribution",
        "solar_power_relative_index",
        "solar_contribution",
        "dry_site_relative_index",
        "dry_site_contribution",
        "water_resource_relative_index",
        "water_resource_contribution",
        "persistent_water_relative_index",
        "persistent_water_contribution",
        "mean_temperature_c",
        "geological_record_count",
    ]

    result = result[columns].sort_values(
        ["mission_profile", "mission_rank", "candidate"]
    ).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    methodology = """# Member 4 — Mission-Specific Screening Profiles

## Purpose

This module combines terrain rank evidence and environmental indicators
into four separate, mission-oriented screening profiles.

## Profiles and initial weights

| Mission profile | Terrain | Solar | Dry-site | Water | Persistent water |
|---|---:|---:|---:|---:|---:|
| Lunar rover mobility | 80% | 20% | — | — | — |
| Lunar polar operations | 35% | 35% | — | 30% | — |
| Mars rover mobility | 75% | 10% | 15% | — | — |
| Lunar resource prospecting | 20% | — | — | 60% | 20% |

## Interpretation

- Scores are weighted screening indices on a 0–100 scale.
- Rankings are only among the six available Earth candidates.
- Terrain contribution uses ordinal rank position, not physical
  similarity magnitude.
- Weights are initial assumptions and require mission-expert review.
- Scores are not probabilities, measured mission success rates,
  or proof of physical equivalence.

## Important limitations

- Earth water occurrence is not evidence of lunar ice.
- Persistent Earth water is not a direct lunar resource measurement.
- Earth solar irradiance is not equivalent to lunar polar illumination.
- Earth aerosol optical depth is not a direct measure of Martian dust.
- Geological record count is evidence coverage only, not mineral
  abundance, diversity, or resource value.
- Temperature is reported separately because no validated target
  operating range was supplied.
- Terrain comparisons use latitude-band planetary averages and
  have resolution and aggregation limitations.

These profiles are preliminary comparative screening tools.
They must not be interpreted as validated mission-site selections.
"""

    REPORT.write_text(methodology, encoding="utf-8")

    print("\nMEMBER 4 — MISSION PROFILE SCORING COMPLETE")
    print("Candidates:", result["candidate"].nunique())
    print("Mission profiles:", result["mission_profile"].nunique())
    print("Total scored records:", len(result))

    for profile_name in PROFILES:
        print(f"\n{profile_name}:")
        print(
            result[result["mission_profile"] == profile_name][
                ["candidate", "mission_screening_score", "mission_rank"]
            ].to_string(index=False)
        )

    print("\nSaved:", OUTPUT)
    print("Methodology:", REPORT)


if __name__ == "__main__":
    main()
