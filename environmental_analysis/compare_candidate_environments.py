from pathlib import Path
import pandas as pd

source = Path(
    "data/processed/earth_candidate_profiles/"
    "integrated_earth_candidate_profiles_complete.csv"
)

out = Path("data/processed/environmental_comparison")
out.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source)

metrics = {
    "mean_temperature_c": "Mean annual temperature (2020)",
    "mean_solar_irradiance_w_m2": "Mean solar irradiance",
    "annual_mean_aod_55": "Mean aerosol optical depth",
    "mean_water_occurrence_percent": "Mean surface-water occurrence",
    "pixels_with_detected_water_percent": "Pixels with detected water",
    "persistent_water_pixels_percent": "Persistent water pixels",
    "geological_record_count": "Geological record count",
    "terrain_slope_mean_degrees": "Mean terrain slope",
    "terrain_roughness_630m_mean": "Mean terrain roughness at 630m",
    "terrain_hidden_ruggedness_percent": "Hidden ruggedness",
}

available = {
    col: label for col, label in metrics.items()
    if col in df.columns
}

if len(df) != 6:
    raise ValueError(f"Expected 6 candidates, found {len(df)}")

if df["candidate"].nunique() != 6:
    raise ValueError("Candidate names are not unique.")

if not available:
    raise ValueError("No expected comparison metrics found.")

summary = df[["candidate"] + list(available)].copy()

summary.to_csv(
    out / "six_candidate_environmental_comparison.csv",
    index=False
)

ranking_rows = []

for column, label in available.items():
    valid = df[["candidate", column]].dropna()

    for _, row in valid.iterrows():
        ranking_rows.append({
            "metric": label,
            "candidate": row["candidate"],
            "value": row[column],
            "rank_highest": valid[column].rank(
                ascending=False, method="min"
            ).loc[row.name]
        })

rankings = pd.DataFrame(ranking_rows)
rankings.to_csv(
    out / "candidate_environmental_metric_rankings.csv",
    index=False
)

report = [
    "# TERRATIME4D — Six-Candidate Environmental Comparison",
    "",
    "## Dataset overview",
    f"- Candidate locations: {len(df)}",
    f"- Integrated columns: {len(df.columns)}",
    f"- Metrics compared: {len(available)}",
    "",
    "## Comparative findings",
]

for column, label in available.items():
    valid = df[["candidate", column]].dropna()

    if valid.empty:
        continue

    highest = valid.loc[valid[column].idxmax()]
    lowest = valid.loc[valid[column].idxmin()]

    report.extend([
        f"### {label}",
        f"- Highest: {highest['candidate']} ({highest[column]:.4f})",
        f"- Lowest: {lowest['candidate']} ({lowest[column]:.4f})",
        ""
    ])

report.extend([
    "## Scientific interpretation and limitations",
    "- Rankings are descriptive comparisons, not mission-suitability scores.",
    "- NASA POWER climate and solar values represent 2020, not long-term climate normals.",
    "- Aerosol optical depth measures total aerosol loading, not dust alone.",
    "- JRC surface-water occurrence represents historical observations from 1984–2024.",
    "- Geological record counts reflect database records, not mineral abundance.",
    "- Terrain metrics are derived from static elevation data.",
    "- Missing or unavailable environmental categories must not be interpreted as zero.",
    "",
    "## Data completeness",
])

for column in available:
    report.append(
        f"- {column}: {df[column].notna().sum()}/6 candidates populated"
    )

(out / "six_candidate_environmental_comparison.md").write_text(
    "\n".join(report), encoding="utf-8"
)

print("\nENVIRONMENTAL COMPARISON COMPLETE")
print("Candidates:", len(df))
print("Metrics:", len(available))
print("\n", summary.to_string(index=False))
print("\nSaved outputs:")
print(out / "six_candidate_environmental_comparison.csv")
print(out / "candidate_environmental_metric_rankings.csv")
print(out / "six_candidate_environmental_comparison.md")
