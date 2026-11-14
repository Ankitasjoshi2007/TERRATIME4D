from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

EARTH_FILE = ROOT / "data/processed/combined_priority_candidate_terrain.csv"
PLANET_FILE = ROOT / "results/member3_global_analysis_v3/moon_mars_latitude_band_analysis_v3.csv"

OUT_DIR = ROOT / "results/member4_similarity_scoring"
OUT_FILE = OUT_DIR / "terrain_similarity_scores.csv"
REPORT_FILE = OUT_DIR / "terrain_similarity_methodology.md"


def latitude_band(latitude):
    lower = int(latitude // 10) * 10
    return f"{lower} to {lower + 10}"


def main():
    earth = pd.read_csv(EARTH_FILE)
    planets = pd.read_csv(PLANET_FILE)

    earth["latitude_band"] = earth["latitude"].apply(latitude_band)

    merged = earth.merge(
        planets,
        on="latitude_band",
        how="left",
        validate="many_to_many"
    )

    if merged["slope_mean_degrees_y"].isna().any():
        raise ValueError("Missing planetary latitude-band matches.")

    merged["mean_slope_difference_degrees"] = (
        merged["slope_mean_degrees_x"] - merged["slope_mean_degrees_y"]
    ).abs()

    merged["p90_slope_difference_degrees"] = (
        merged["slope_90th_percentile_degrees"] - merged["slope_p90_degrees"]
    ).abs()

    # Equal-weight descriptive difference between the two slope statistics.
    merged["combined_slope_difference_degrees"] = (
        merged["mean_slope_difference_degrees"]
        + merged["p90_slope_difference_degrees"]
    ) / 2

    output = merged[[
        "location", "latitude", "latitude_band", "planet",
        "slope_mean_degrees_x", "slope_mean_degrees_y",
        "slope_90th_percentile_degrees", "slope_p90_degrees",
        "mean_slope_difference_degrees",
        "p90_slope_difference_degrees",
        "combined_slope_difference_degrees"
    ]].rename(columns={
        "location": "candidate",
        "slope_mean_degrees_x": "earth_slope_mean_degrees",
        "slope_mean_degrees_y": "planetary_band_slope_mean_degrees",
        "slope_90th_percentile_degrees": "earth_slope_p90_degrees",
        "slope_p90_degrees": "planetary_band_slope_p90_degrees"
    })

    output["rank_within_planet"] = (
        output.groupby("planet")["combined_slope_difference_degrees"]
        .rank(method="min", ascending=True)
        .astype(int)
    )

    output = output.sort_values(
        ["planet", "rank_within_planet", "candidate"]
    ).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUT_FILE, index=False)

    report = """# TERRATIME4D — Member 4 Terrain Comparison

## Slope difference method

Each Earth candidate is matched to the Moon and Mars reference latitude
band containing its latitude.

For each comparison:

- Mean slope difference = absolute difference between the two mean slopes.
- P90 slope difference = absolute difference between the two 90th-percentile slopes.
- Combined slope difference = arithmetic mean of those two differences.

All differences are expressed in degrees. Candidates are ranked separately
for the Moon and Mars, with the smallest difference ranked first.

## Scientific limitations

- This is a descriptive slope comparison, not a mission-suitability score.
- Planetary values are latitude-band averages, not exact local-site measurements.
- Earth and planetary datasets have different spatial resolutions and
  processing histories.
- Roughness is excluded because the available measurements use incompatible
  spatial scales.
- Elevation is excluded because the available elevation datums are not
  directly comparable.
- The two slope statistics receive equal weight as an initial descriptive
  comparison, not as a calibrated scientific weighting.
- These results do not establish physical equivalence between Earth and
  lunar or Martian environments.

A future mission-specific score requires validated criteria and weights.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print("\nMEMBER 4 — SLOPE COMPARISON COMPLETE")
    print("Candidates:", earth["location"].nunique())
    print("Comparisons:", len(output))
    print("\nRankings (lower difference is closer):")
    print(output[[
        "candidate", "planet",
        "combined_slope_difference_degrees",
        "rank_within_planet"
    ]].to_string(index=False))
    print("\nSaved:", OUT_FILE)
    print("Methodology:", REPORT_FILE)


if __name__ == "__main__":
    main()
