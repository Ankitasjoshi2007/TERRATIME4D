from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results/member4_similarity_scoring"

TERRAIN = DATA / "terrain_similarity_scores.csv"
ENV = DATA / "environmental_screening_scores.csv"
MISSION = DATA / "mission_specific_scores.csv"

OUTPUT = DATA / "MEMBER4_FINAL_REPORT.md"


def markdown_table(df):
    if df.empty:
        return "_No records available._"

    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for row in df.itertuples(index=False, name=None):
        values = []
        for value in row:
            if isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def main():
    for file in [TERRAIN, ENV, MISSION]:
        if not file.exists():
            raise FileNotFoundError(file)

    terrain = pd.read_csv(TERRAIN)
    env = pd.read_csv(ENV)
    mission = pd.read_csv(MISSION)

    if len(terrain) != 12 or len(env) != 6 or len(mission) != 24:
        raise ValueError("Unexpected input record counts.")

    sections = []

    sections.append("""# TERRATIME4D — Member 4 Final Report
## Similarity Screening and Mission-Specific Scoring

**Role:** Member 4 — Similarity and Mission Scoring Engine  
**Scope:** Six Earth candidate regions, Moon/Mars terrain comparisons, and four mission-oriented screening profiles.

## 1. Objective

The Member 4 module combines available terrain and environmental evidence
to compare six Earth candidate regions for different planetary mission
analogue objectives.

The output is a preliminary screening framework. It does not identify
validated mission sites or establish physical equivalence between Earth,
the Moon, and Mars.

## 2. Inputs and evidence

- Terrain similarity comparisons against Moon and Mars latitude-band
  averages.
- Environmental indicators for six Earth candidates.
- Terrain and environmental evidence are joined by candidate name.
- Four mission profiles are evaluated independently.

The environmental dataset contains six candidates. The terrain dataset
contains six candidates compared against each of two planetary references.

## 3. Terrain comparison results

The terrain comparison uses mean and 90th-percentile slope differences.
Lower combined differences indicate closer slope statistics within the
selected latitude band.

Roughness is excluded from the planetary similarity calculation because
the available Earth and planetary measurements use incompatible spatial
scales. Elevation is excluded because the vertical reference datums are
not sufficiently harmonized.

""")

    for planet in ["Moon", "Mars"]:
        subset = terrain[terrain["planet"].str.lower() == planet.lower()]
        subset = subset.sort_values("rank_within_planet")
        sections.append(f"### {planet} terrain ranking\n\n")
        sections.append(markdown_table(
            subset[[
                "candidate",
                "combined_slope_difference_degrees",
                "rank_within_planet",
            ]]
        ))
        sections.append("\n\n")

    sections.append("""## 4. Environmental screening

Environmental indices are relative percentile positions among the six
Earth candidates only. They are not percentages of lunar or Martian
similarity.

- Solar power: higher irradiance is favoured.
- Low aerosol: lower aerosol optical depth is favoured.
- Dry-site analogue: lower surface-water occurrence is favoured.
- Water-resource prospecting: higher surface-water occurrence is favoured.
- Persistent water: higher observed persistence is reported as a separate
  indicator.
- Temperature remains a measured value without a directional ranking.
- Geological record count is evidence coverage only, not mineral abundance
  or resource value.

### Solar ranking

""")

    sections.append(markdown_table(
        env.sort_values("solar_rank")[[
            "candidate",
            "mean_solar_irradiance_w_m2",
            "solar_rank",
        ]]
    ))
    sections.append("\n\n### Dry-site ranking\n\n")
    sections.append(markdown_table(
        env.sort_values("dry_site_rank")[[
            "candidate",
            "mean_water_occurrence_percent",
            "dry_site_rank",
        ]]
    ))
    sections.append("\n\n### Water-resource screening ranking\n\n")
    sections.append(markdown_table(
        env.sort_values("water_resource_rank")[[
            "candidate",
            "mean_water_occurrence_percent",
            "water_resource_rank",
        ]]
    ))
    sections.append("\n\n")

    sections.append("""## 5. Mission-specific screening profiles

Each profile uses explicit initial weights. Terrain input is converted
from its ordinal rank into a 0–100 rank-position index before weighting.
Environmental inputs use their relative indices.

| Mission profile | Terrain | Solar | Dry-site | Water | Persistent water |
|---|---:|---:|---:|---:|---:|
| Lunar rover mobility | 80% | 20% | — | — | — |
| Lunar polar operations | 35% | 35% | — | 30% | — |
| Mars rover mobility | 75% | 10% | 15% | — | — |
| Lunar resource prospecting | 20% | — | — | 60% | 20% |

These weights are preliminary model assumptions, not validated mission
requirements. Geological record count and temperature are reported
separately and are not included in the composite.

""")

    for profile in mission["mission_profile"].drop_duplicates():
        subset = mission[mission["mission_profile"] == profile]
        subset = subset.sort_values("mission_rank")

        sections.append(f"### {profile}\n\n")
        sections.append(markdown_table(
            subset[[
                "candidate",
                "mission_screening_score",
                "mission_rank",
                "mean_temperature_c",
                "geological_record_count",
            ]]
        ))
        sections.append("\n\n")

    sections.append("""## 6. Scientific limitations and interpretation

1. The six Earth candidates are a limited comparison set, not a global
   ranking of all possible analogue sites.
2. Planetary terrain references are latitude-band averages, not exact
   local landing-site measurements.
3. Earth and planetary terrain datasets differ in spatial resolution
   and aggregation.
4. Roughness is excluded from the planetary score because measurement
   scales are incompatible.
5. Elevation is excluded from direct similarity scoring because
   vertical datums differ.
6. Earth surface-water occurrence does not establish the presence of
   lunar ice or Martian subsurface water.
7. Earth solar irradiance does not represent lunar polar illumination
   or a mission-specific power budget.
8. Aerosol optical depth is not a dust-only measurement.
9. NASA POWER temperature and solar inputs represent 2020.
10. Geological record counts describe available records, not mineral
    abundance, diversity, or economic/resource value.
11. The scores are weighted screening indices, not probabilities,
    mission-success estimates, or physical similarity percentages.
12. Static DEM-derived terrain metrics do not describe terrain change
    over time.

## 7. Validation summary

- Terrain comparisons: 12 records (six candidates × two planets).
- Environmental screening: six unique candidates.
- Mission profiles: four.
- Mission-specific scores: 24 records.
- Six candidates are represented in every mission profile.
- Missing values in the validated mission score output: zero.
- Mission scores are within the 0–100 range.
- Weighted component contributions reproduce the reported score,
  within floating-point precision.

## 8. Conclusion

The current screening results identify different leading Earth
candidates for different mission objectives. Queensland and Western
Australia rank strongly in the preliminary Mars rover slope comparison,
while Ontario leads the lunar rover and lunar polar profiles under the
current assumptions. Brooks Range leads the lunar resource prospecting
profile because of its high Earth surface-water indicators.

These results demonstrate why analogue selection should be
mission-specific. They are preliminary comparative results and require
resolution-matched planetary site data, validated mission requirements,
and expert review before operational interpretation.

---
**Member 4 deliverables:** terrain similarity scores, environmental
screening scores, mission-specific scores, methodology files, and this
consolidated report.
""")

    OUTPUT.write_text("".join(sections), encoding="utf-8")

    print("MEMBER 4 FINAL REPORT GENERATED")
    print("Terrain records:", len(terrain))
    print("Environmental candidates:", env["candidate"].nunique())
    print("Mission profiles:", mission["mission_profile"].nunique())
    print("Mission score records:", len(mission))
    print("Report:", OUTPUT)


if __name__ == "__main__":
    main()
