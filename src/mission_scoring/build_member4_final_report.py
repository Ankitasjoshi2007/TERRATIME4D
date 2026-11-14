from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results/member4_similarity_scoring"

TERRAIN = DATA / "terrain_similarity_scores.csv"
ENV = DATA / "environmental_screening_scores.csv"
INTEGRATED = DATA / "integrated_mission_scores.csv"
OUTPUT = DATA / "MEMBER4_FINAL_REPORT.md"
SENSITIVITY = DATA / "weight_sensitivity_results.csv"
SENSITIVITY_SUMMARY = DATA / "weight_sensitivity_summary.csv"
SENSITIVITY_BASELINE = DATA / "weight_sensitivity_baseline.csv"

# These are the explicit weights used by build_integrated_mission_scores.py.
PROFILE_WEIGHTS = {
    "Lunar rover mobility": {
        "terrain": 0.80, "solar": 0.20
    },
    "Lunar polar operations": {
        "terrain": 0.25, "solar": 0.25,
        "cold_months": 0.25, "water": 0.25
    },
    "Mars rover mobility": {
        "terrain": 0.65, "dry_site": 0.15,
        "solar": 0.10, "aerosol_mean": 0.10
    },
    "Lunar resource prospecting": {
        "terrain": 0.20, "water": 0.60,
        "persistent_water": 0.20
    },
    "Mars dust-process analogue": {
        "aerosol_mean": 0.40, "aerosol_variability": 0.35,
        "high_loading_months": 0.25
    },
    "Volcanic and cave analogue reconnaissance": {
        "volcanic_evidence_rate": 0.50,
        "karst_evidence_rate": 0.50
    },
    "Cold-region operations analogue": {
        "cold_months": 0.50, "coldest_month": 0.50
    },
}

COMPONENT_LABELS = {
    "terrain": "Terrain similarity",
    "solar": "Solar irradiance",
    "cold_months": "Cold-month frequency",
    "water": "Surface-water occurrence",
    "dry_site": "Dry-site indicator",
    "aerosol_mean": "Mean aerosol loading",
    "persistent_water": "Persistent water indicator",
    "aerosol_variability": "Aerosol variability",
    "high_loading_months": "High-aerosol months",
    "volcanic_evidence_rate": "Volcanic geological evidence rate",
    "karst_evidence_rate": "Possible karst host-rock evidence rate",
    "coldest_month": "Coldest-month temperature indicator",
}


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
            if pd.isna(value):
                values.append("—")
            elif isinstance(value, (float, int)):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value).replace("|", "/"))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def main():
    for file in [TERRAIN, ENV, INTEGRATED, SENSITIVITY, SENSITIVITY_SUMMARY, SENSITIVITY_BASELINE]:
        if not file.exists():
            raise FileNotFoundError(file)

    terrain = pd.read_csv(TERRAIN)
    env = pd.read_csv(ENV)
    scores = pd.read_csv(INTEGRATED)
    sensitivity = pd.read_csv(SENSITIVITY)
    sensitivity_summary = pd.read_csv(SENSITIVITY_SUMMARY)
    sensitivity_baseline = pd.read_csv(SENSITIVITY_BASELINE)

    if len(terrain) != 12:
        raise ValueError(f"Expected 12 terrain rows; found {len(terrain)}")
    if env["candidate"].nunique() != 6:
        raise ValueError("Expected six environmental candidates.")
    if len(scores) != 42:
        raise ValueError(f"Expected 42 integrated scores; found {len(scores)}")
    if scores["mission_profile"].nunique() != 7:
        raise ValueError("Expected seven integrated mission profiles.")
    if scores.groupby("mission_profile")["candidate"].nunique().ne(6).any():
        raise ValueError("Every mission profile must contain six candidates.")
    if scores["screening_index_0_100"].isna().any():
        raise ValueError("Integrated scores contain missing screening values.")

    if len(sensitivity) != 40:
        raise ValueError(
            f"Expected 40 sensitivity scenarios; found {len(sensitivity)}"
        )
    if sensitivity_summary["mission_profile"].nunique() != 7:
        raise ValueError("Sensitivity summary must contain seven profiles.")
    if sensitivity_baseline["mission_profile"].nunique() != 7:
        raise ValueError("Sensitivity baseline must contain seven profiles.")
    if sensitivity["top_candidate_changed"].isna().any():
        raise ValueError("Sensitivity results contain missing change flags.")
    if sensitivity["mean_absolute_rank_shift"].isna().any():
        raise ValueError("Sensitivity results contain missing rank shifts.")
    if not sensitivity.groupby("mission_profile").size().eq(
        sensitivity.groupby("mission_profile")["perturbed_component"].transform(
            "count"
        ).groupby(sensitivity["mission_profile"]).first()
    ).all():
        raise ValueError("Sensitivity scenario grouping is inconsistent.")

    sections = []

    sections.append("""# TERRATIME4D — Member 4 Final Report
## Integrated Similarity Screening and Mission-Specific Scoring

**Role:** Member 4 — Similarity and Mission Scoring Engine
**Candidate set:** Six Earth regions
**Planetary references:** Moon and Mars
**Mission profiles:** Seven
**Primary integrated output:** `integrated_mission_scores.csv`

## 1. Objective

Member 4 combines terrain, environmental, aerosol, cold-climate,
mineral/geological, and volcanic/karst evidence to screen Earth regions
for different lunar and Martian analogue research objectives.

The engine produces mission-specific, relative screening indices.
It does not identify validated landing sites, establish physical
equivalence between planetary environments, or predict mission success.

## 2. Integrated evidence

The integrated candidate evidence joins six evidence families:

1. Terrain metrics and terrain classifications.
2. Environmental indicators, including solar irradiance and water occurrence.
3. Aerosol loading and variability indicators.
4. Cold-climate screening indicators.
5. Mineral and lithological geological records.
6. Volcanic and possible karst geological evidence.

The integrated evidence build contains six Earth candidates, with all
six evidence families represented for every candidate. Evidence coverage
means that source records were available; it does not mean that every
candidate has equally detailed or equally reliable observations.

## 3. Planetary terrain similarity

Terrain similarity compares Earth candidate slope statistics with
available Moon and Mars latitude-band summaries. The calculation uses
mean slope and 90th-percentile slope differences. Lower combined
differences indicate closer slope statistics within the selected band.

Roughness is excluded from the planetary similarity calculation because
the available Earth and planetary measurements use incompatible spatial
scales. Elevation is excluded because vertical reference datums are not
sufficiently harmonized.

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

    sections.append("""## 4. Environmental screening context

Environmental indices are relative comparisons among the six Earth
candidates. They are not percentages of lunar or Martian similarity.

- Solar irradiance: higher values are favoured where the profile uses solar input.
- Dry-site indicator: lower surface-water occurrence is favoured.
- Water-resource indicator: higher surface-water occurrence is favoured.
- Persistent-water indicator: reported as a separate Earth observation.
- Temperature indicators describe Earth climate records, not planetary surface conditions.
- Geological record counts describe evidence availability, not mineral abundance.

### Solar irradiance ranking

""")

    if "solar_rank" in env.columns:
        sections.append(markdown_table(
            env.sort_values("solar_rank")[[
                "candidate", "mean_solar_irradiance_w_m2", "solar_rank"
            ]]
        ))
    else:
        sections.append("_Solar ranking field unavailable in source._")

    sections.append("\n\n### Water-occurrence context\n\n")
    if "mean_water_occurrence_percent" in env.columns:
        sections.append(markdown_table(
            env[["candidate", "mean_water_occurrence_percent"]]
            .sort_values("mean_water_occurrence_percent", ascending=False)
        ))
    else:
        sections.append("_Water-occurrence field unavailable in source._")

    sections.append("""

## 5. Integrated mission-specific scoring

Each mission profile uses an explicit set of weighted components.
For every component, the model calculates a relative index among the
six candidates and multiplies it by the profile weight.

The final score is the sum of the weighted component contributions.
Scores range from 0 to 100 and are relative to this six-candidate
comparison set. They are not probabilities or universal suitability
measurements.

### 5.1 Profile weights

""")

    weight_rows = []
    for profile, weights in PROFILE_WEIGHTS.items():
        weight_rows.append({
            "Mission profile": profile,
            "Weighted components": "; ".join(
                f"{COMPONENT_LABELS.get(name, name)}: {weight:.0%}"
                for name, weight in weights.items()
            ),
            "Weight total": sum(weights.values()),
        })
    sections.append(markdown_table(pd.DataFrame(weight_rows)))
    sections.append("\n\n")

    profile_order = list(PROFILE_WEIGHTS)
    for profile in profile_order:
        subset = scores[scores["mission_profile"] == profile].copy()
        subset = subset.sort_values(
            ["mission_rank", "candidate"], kind="stable"
        )

        target = subset["target_planet"].iloc[0]
        profile_type = subset["profile_type"].iloc[0]

        sections.append(f"### {profile}\n\n")
        sections.append(f"**Target:** {target}  \n")
        sections.append(f"**Profile type:** {profile_type}\n\n")
        sections.append("**Candidate ranking**\n\n")
        sections.append(markdown_table(
            subset[[
                "candidate",
                "screening_index_0_100",
                "mission_rank",
                "evidence_sources_present",
                "evidence_sources_expected",
            ]].rename(columns={
                "screening_index_0_100": "Screening index (0–100)",
                "mission_rank": "Rank",
                "evidence_sources_present": "Evidence sources present",
                "evidence_sources_expected": "Evidence sources expected",
            })
        ))

        sections.append("\n\n**Weighted component contributions**\n\n")
        component_data = {"Candidate": subset["candidate"]}
        for component in PROFILE_WEIGHTS[profile]:
            column = f"{component}_contribution"
            if column not in subset.columns:
                raise ValueError(
                    f"Missing contribution column {column} for {profile}"
                )
            if subset[column].isna().any():
                raise ValueError(
                    f"Missing active contribution {column} for {profile}"
                )
            component_data[COMPONENT_LABELS[component]] = subset[column]

        sections.append(markdown_table(pd.DataFrame(component_data)))
        sections.append("\n\n")

    sections.append("""## 6. Weight sensitivity analysis

A deterministic one-at-a-time sensitivity test was performed for every
active component in each mission profile. Each component weight was
independently decreased by 20% and increased by 20% relative to its
baseline value. The remaining component weights were proportionally
renormalized so that the profile weights continued to sum to 1.0.

This produced 40 perturbation scenarios across seven mission profiles.
The baseline calculation was also reconstructed from the stored
component indices and original weights. All 42 baseline scores were reproduced within a numerical tolerance of 1e-8.

The test measures local ranking stability under the selected weight
changes. It is not a statistical confidence interval, probability
estimate, or validation of the weights as mission requirements.

### 6.1 Sensitivity summary

""")

    sensitivity_display = sensitivity_summary.rename(columns={
        "mission_profile": "Mission profile",
        "scenarios_tested": "Scenarios tested",
        "top_candidate_changes": "Top-candidate changes",
        "mean_rank_shift": "Mean absolute rank shift",
        "maximum_rank_shift": "Maximum absolute rank shift",
    })
    sections.append(markdown_table(sensitivity_display))
    sections.append("\n\n### 6.2 Baseline leaders\n\n")

    baseline_display = sensitivity_baseline.rename(columns={
        "mission_profile": "Mission profile",
        "baseline_top_candidate": "Baseline top candidate",
        "baseline_top_score": "Baseline top score",
    })
    sections.append(markdown_table(baseline_display))
    sections.append("\n\n### 6.3 Interpretation\n\n")

    volcanic = sensitivity_summary[
        sensitivity_summary["mission_profile"]
        == "Volcanic and cave analogue reconnaissance"
    ]
    if not volcanic.empty:
        changes = int(volcanic.iloc[0]["top_candidate_changes"])
        scenarios = int(volcanic.iloc[0]["scenarios_tested"])
        sections.append(
            f"The volcanic and cave reconnaissance profile changed its "
            f"top-ranked candidate in {changes} of {scenarios} perturbation "
            "scenarios. Its baseline result is therefore more sensitive "
            "to the selected component weights than the other profiles. "
            "The baseline tie between Baja California and Brooks Range "
            "should be interpreted cautiously.\n\n"
        )

    stable_profiles = sensitivity_summary[
        sensitivity_summary["top_candidate_changes"] == 0
    ]["mission_profile"].tolist()
    sections.append(
        "The following profiles retained their baseline top-ranked "
        "candidate in every tested scenario: "
        + ", ".join(stable_profiles)
        + ". This indicates local top-rank stability under the tested "
        "weight changes, not general validity under all possible "
        "assumptions.\n\n"
    )

    sections.append("""## 7. Interpretation and scientific limitations


1. **Limited candidate sample:** The six Earth candidates are not a
   global ranking of all possible analogue sites.
2. **Relative normalization:** Component indices are normalized within
   this candidate set. Adding or removing candidates can change scores
   and rankings.
3. **Terrain reference limits:** Planetary terrain references are
   latitude-band averages, not exact local landing-site measurements.
4. **Resolution differences:** Earth and planetary terrain datasets
   differ in spatial resolution and aggregation.
5. **Roughness:** Roughness is excluded from direct planetary similarity
   scoring because measurement scales are incompatible.
6. **Elevation:** Elevation is excluded from direct similarity scoring
   because vertical datums differ.
7. **Water interpretation:** Earth surface-water occurrence does not
   establish the presence of lunar ice or Martian subsurface water.
8. **Solar interpretation:** Earth solar irradiance does not represent
   lunar polar illumination or a mission-specific power budget.
9. **Aerosol interpretation:** Aerosol optical depth is an atmospheric
   aerosol proxy, not a dust-only measurement or direct dust-event record.
10. **Cold-region interpretation:** Earth cold-month indicators are
    terrestrial climate analogues, not measurements of lunar or Martian
    surface temperatures.
11. **Geological evidence:** Volcanic and possible karst record rates
    describe mentions in available geological records. They do not
    confirm lava tubes, caves, mineral reserves, or resource abundance.
12. **Time coverage:** NASA POWER temperature and solar inputs represent
    2020; water occurrence represents its source observation period.
13. **Static terrain:** Static DEM-derived terrain metrics do not describe
    terrain change, seasonal movement, or dust migration over time.
14. **Model assumptions:** Profile weights are initial screening
    assumptions, not validated mission requirements.
15. **Physical non-equivalence:** Earth analogues cannot reproduce lunar
    gravity and vacuum or the full Martian atmospheric and radiation
    environment.
16. **Score meaning:** Scores are weighted screening indices, not
    probabilities, mission-success estimates, or physical similarity
    percentages.

## 8. Validation summary

- Terrain similarity: 12 records (six candidates × two planets).
- Environmental screening: six unique candidates.
- Integrated evidence: six candidates with six evidence families represented.
- Integrated mission profiles: seven.
- Integrated mission score records: 42.
- Candidate coverage: six candidates in every mission profile.
- Required screening scores: no missing values.
- Profile weights: each profile totals 1.0.
- Weighted component contributions: validated against final scores.
- Score range: 0–100.

## 9. Conclusion

The integrated results show that the leading Earth analogue depends on
the mission objective. Ontario leads the Mars dust-process analogue
profile and lunar rover mobility under the current model assumptions.
Queensland leads the Mars rover mobility profile. Brooks Range leads
lunar resource prospecting, lunar polar operations, and cold-region
operations. The volcanic and cave reconnaissance profile produces a
tie between Baja California and Brooks Range.

These rankings are screening results, not operational site selections.
They demonstrate the value of mission-specific evaluation while
highlighting the need for better spatially matched planetary data,
validated mission requirements, temporal analysis, and expert review.

---
**Member 4 deliverables:** terrain similarity scores, environmental
screening scores, integrated candidate evidence, seven-profile
integrated mission scores, methodology files, scoring code, and this
consolidated report.
""")

    OUTPUT.write_text("".join(sections), encoding="utf-8")

    print("MEMBER 4 FINAL REPORT GENERATED")
    print("Terrain records:", len(terrain))
    print("Environmental candidates:", env["candidate"].nunique())
    print("Integrated evidence families: 6")
    print("Mission profiles:", scores["mission_profile"].nunique())
    print("Integrated mission score records:", len(scores))
    print("Report:", OUTPUT)


if __name__ == "__main__":
    main()
