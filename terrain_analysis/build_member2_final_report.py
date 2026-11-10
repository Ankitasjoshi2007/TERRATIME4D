from pathlib import Path
import pandas as pd

root = Path("data/processed/global_terrain")
folder = root / "rover_screening"

advanced = pd.read_csv(root / "global_advanced_terrain_summary.csv")
rover = pd.read_csv(folder / "global_rover_screening_summary.csv")
ranking = pd.read_csv(folder / "global_rover_terrain_ranking.csv")
shortlist = pd.read_csv(folder / "geographic_candidate_shortlist.csv")

if len(advanced) != 645 or len(rover) != 645 or len(ranking) != 645:
    raise SystemExit("Expected 645 records in each global dataset. Report not written.")

if advanced["location"].nunique() != 645:
    raise SystemExit("Duplicate or missing advanced-terrain tile identifiers.")

for col in [
    "lower_relief_screen_percent",
    "intermediate_screen_percent",
    "challenging_terrain_percent"
]:
    rover[col] = pd.to_numeric(rover[col], errors="coerce")

if rover[[
    "lower_relief_screen_percent",
    "intermediate_screen_percent",
    "challenging_terrain_percent"
]].isna().any().any():
    raise SystemExit("Missing rover screening percentages.")

out = root / "MEMBER2_TERRAIN_ANALYSIS_FINAL_REPORT.md"

top_nonpolar = shortlist[
    shortlist["geographic_group"] == "Non-polar"
].sort_values("rover_screening_score_100", ascending=False).head(10)

top_polar = shortlist[
    shortlist["geographic_group"] == "Polar"
].sort_values("rover_screening_score_100", ascending=False).head(10)

def table(frame, columns):
    return frame[columns].to_string(index=False)

with out.open("w", encoding="utf-8") as f:
    f.write("# TERRATIME4D — Member 2: Global Terrain Analysis Report\n\n")

    f.write("## 1. Objective\n\n")
    f.write(
        "The objective was to process Copernicus GLO-90 elevation data, "
        "derive terrain characteristics, classify surface morphology, "
        "and screen terrain tiles for preliminary rover mobility and "
        "landing-study relevance.\n\n"
    )

    f.write("## 2. Global processing coverage\n\n")
    f.write(f"- Advanced terrain summary records: **{len(advanced)}**\n")
    f.write(f"- Rover screening records: **{len(rover)}**\n")
    f.write(f"- Ranked terrain tiles: **{len(ranking)}**\n")
    f.write("- Advanced terrain raster outputs: 645, each containing 10 bands.\n")
    f.write("- Local-relief scales: 270 m, 630 m and 1,350 m.\n\n")

    f.write("## 3. Terrain measurements\n\n")
    f.write(
        "The analysis derives slope in degrees, local elevation roughness "
        "at three spatial scales, local relief at three scales, hidden "
        "ruggedness indicators and terrain-transition hotspot indicators.\n\n"
    )
    f.write(
        "Local roughness represents neighbourhood elevation variability. "
        "Local relief represents the neighbourhood elevation range "
        "(maximum minus minimum).\n\n"
    )

    f.write("## 4. Terrain classification\n\n")
    f.write(
        "Terrain classification outputs are available in "
        "`global_terrain_classification_summary.csv` and "
        "`classification_rasters/`. The classification distinguishes "
        "flat/smooth, rolling, rugged, relative ridge and relative valley "
        "terrain using the implemented TPI-based method.\n\n"
    )

    f.write("## 5. Rover terrain screening\n\n")
    f.write(
        "Exploratory pixel thresholds were applied: lower-relief "
        "(slope <= 5 degrees and 630 m roughness <= 2 m), intermediate "
        "(slope <= 15 degrees and roughness <= 5 m, excluding lower-relief), "
        "and challenging (remaining valid pixels).\n\n"
    )
    f.write(
        "| Tile-level percentage measure | Mean across 645 tiles |\n"
        "|---|---:|\n"
    )
    for col, label in [
        ("lower_relief_screen_percent", "Lower-relief"),
        ("intermediate_screen_percent", "Intermediate"),
        ("challenging_terrain_percent", "Challenging")
    ]:
        f.write(f"| {label} | {rover[col].mean():.2f}% |\n")
    f.write(
        "\nThese are unweighted averages of tile-level percentages, "
        "not pixel-weighted global surface estimates.\n\n"
    )

    f.write("## 6. Global ranking method\n\n")
    f.write(
        "Tiles were ranked using a weighted relative score: slope 35%, "
        "630 m roughness 25%, 630 m local relief 20%, and lower-relief "
        "screening share 20%. The score is a comparative screening index "
        "within this dataset, not a probability or certified site rating.\n\n"
    )

    f.write("## 7. Geographic candidate groups\n\n")
    f.write(
        f"- Polar candidates (absolute latitude >= 60 degrees): "
        f"**{(shortlist['geographic_group'] == 'Polar').sum()} shortlisted**\n"
    )
    f.write(
        f"- Non-polar candidates (absolute latitude < 60 degrees): "
        f"**{(shortlist['geographic_group'] == 'Non-polar').sum()} shortlisted**\n\n"
    )

    f.write("### Top 10 non-polar candidates\n\n")
    f.write(table(
        top_nonpolar,
        ["tile", "rover_screening_score_100", "latitude", "longitude"]
    ))
    f.write("\n\n### Top 10 polar candidates\n\n")
    f.write(table(
        top_polar,
        ["tile", "rover_screening_score_100", "latitude", "longitude"]
    ))
    f.write("\n\n")

    f.write("## 8. Interpretation\n\n")
    f.write(
        "The ranking identifies tiles with comparatively favourable "
        "slope, roughness, local-relief and lower-relief screening values. "
        "Separating polar and non-polar groups prevents very low-relief "
        "polar tiles from automatically dominating every candidate list. "
        "The shortlist is a basis for further investigation, not a final "
        "selection of rover landing sites.\n\n"
    )

    f.write("## 9. Limitations\n\n")
    f.write(
        "- Copernicus GLO-90 is a digital surface model; vegetation and "
        "built structures can influence terrain measurements.\n"
        "- A 90 m elevation product cannot resolve every small-scale hazard.\n"
        "- The 645 processed tiles represent sampled coverage, not a "
        "continuous, complete global terrain survey.\n"
        "- Screening thresholds and weights are exploratory and are not "
        "NASA-certified engineering criteria.\n"
        "- Climate, surface material, imagery, illumination, communications, "
        "and mission-specific constraints require separate assessment.\n"
        "- Static DEM metrics describe terrain morphology, not measured "
        "terrain change through time.\n\n"
    )

    f.write("## 10. Output inventory\n\n")
    outputs = [
        "global_advanced_terrain_summary.csv",
        "global_terrain_fingerprints.csv",
        "advanced_rasters/",
        "global_terrain_classification_summary.csv",
        "classification_rasters/",
        "rover_screening/global_rover_screening_summary.csv",
        "rover_screening/global_rover_screening_map.png",
        "rover_screening/global_rover_terrain_ranking.csv",
        "rover_screening/global_rover_terrain_ranking_map.png",
        "rover_screening/geographic_candidate_shortlist.csv",
        "rover_screening/geographic_candidate_shortlist_map.png",
        "rover_screening/CANDIDATE_EVIDENCE_ASSESSMENT.md"
    ]
    for item in outputs:
        f.write(f"- `{item}`\n")

print("MEMBER 2 FINAL REPORT CREATED")
print("Processed terrain tiles:", len(advanced))
print("Ranked tiles:", len(ranking))
print("Report:", out)
