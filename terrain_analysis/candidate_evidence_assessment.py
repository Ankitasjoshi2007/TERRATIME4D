from pathlib import Path
import pandas as pd

folder = Path("data/processed/global_terrain/rover_screening")

ranking = pd.read_csv(folder / "global_rover_terrain_ranking.csv")
shortlist = pd.read_csv(folder / "geographic_candidate_shortlist.csv")

metrics = {
    "p90_slope_degrees": "Slope",
    "p90_roughness_630m_m": "Roughness",
    "local_relief_630m_p90_m": "Local relief",
    "lower_relief_screen_percent": "Lower-relief share"
}

for col in metrics:
    ranking[col] = pd.to_numeric(ranking[col], errors="coerce")
    shortlist[col] = pd.to_numeric(shortlist[col], errors="coerce")

if ranking[list(metrics)].isna().any().any():
    raise SystemExit("Missing terrain measurements in global ranking.")

# Compare every shortlisted tile against all 645 ranked tiles.
for col, label in metrics.items():
    percentile = ranking[col].rank(pct=True)
    lookup = dict(zip(ranking["tile"], percentile))
    shortlist[label + "_standing"] = shortlist["tile"].map(lookup) * 100

    if label != "Lower-relief share":
        shortlist[label + "_standing"] = (
            100 - shortlist[label + "_standing"]
        )

def interpretation(row):
    strengths = [
        label for label in metrics.values()
        if row[label + "_standing"] >= 75
    ]
    return (
        "Relative strengths: " + ", ".join(strengths)
        if strengths else "No individual metric in the strongest quartile"
    )

shortlist["terrain_evidence"] = shortlist.apply(interpretation, axis=1)

display_cols = [
    "group_rank", "tile", "rover_screening_score_100",
    "p90_slope_degrees", "p90_roughness_630m_m",
    "local_relief_630m_p90_m",
    "lower_relief_screen_percent", "terrain_evidence"
]

# Reconstruct group ranks from the existing overall score.
for group in ["Non-polar", "Polar"]:
    subset = shortlist[
        shortlist["geographic_group"] == group
    ].sort_values("rover_screening_score_100", ascending=False).head(15).copy()

    subset.insert(0, "group_rank", range(1, len(subset) + 1))

    output = folder / (
        "top15_" + group.lower().replace("-", "_") + "_evidence.csv"
    )
    subset[display_cols].to_csv(output, index=False, float_format="%.3f")

    print(f"\nTOP {group.upper()} CANDIDATE EVIDENCE")
    print(subset[display_cols].to_string(index=False))
    print("Saved:", output)

report = folder / "CANDIDATE_EVIDENCE_ASSESSMENT.md"

with report.open("w", encoding="utf-8") as f:
    f.write("# Candidate Terrain Evidence Assessment\n\n")
    f.write(
        "Candidates are compared against all 645 ranked tiles. "
        "Standing >=75 indicates a favourable top-quartile relative "
        "position. Lower slope, roughness and local relief are preferred; "
        "higher lower-relief share is preferred.\n\n"
    )
    f.write(
        "These are relative comparisons, not engineering safety limits "
        "or certified landing criteria.\n\n"
    )

    for group in ["Non-polar", "Polar"]:
        subset = shortlist[
            shortlist["geographic_group"] == group
        ].sort_values("rover_screening_score_100", ascending=False).head(15).copy()
        subset.insert(0, "group_rank", range(1, len(subset) + 1))

        f.write(f"## Top {group} candidates\n\n")
        f.write(subset[display_cols].to_string(index=False))
        f.write("\n\n")

    f.write(
        "## Limitations\n\n"
        "- Copernicus GLO-90 is a digital surface model.\n"
        "- Vegetation, buildings, ice and data quality can affect measurements.\n"
        "- Geographic grouping does not establish accessibility or climate suitability.\n"
        "- Candidates require higher-resolution imagery and mission-specific assessment.\n"
    )

print("\nEVIDENCE ASSESSMENT COMPLETE")
print("Report:", report)
