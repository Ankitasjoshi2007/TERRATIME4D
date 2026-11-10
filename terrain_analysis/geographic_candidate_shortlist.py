from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

folder = Path("data/processed/global_terrain/rover_screening")
source = folder / "global_rover_terrain_ranking.csv"
df = pd.read_csv(source)

df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["rover_screening_score_100"] = pd.to_numeric(
    df["rover_screening_score_100"], errors="coerce"
)

df = df.dropna(subset=[
    "latitude", "longitude", "rover_screening_score_100"
]).copy()

df["geographic_group"] = np.where(
    df["latitude"].abs() >= 60,
    "Polar",
    "Non-polar"
)

polar = df[df["geographic_group"] == "Polar"].sort_values(
    "rover_screening_score_100", ascending=False
).head(25)

nonpolar = df[df["geographic_group"] == "Non-polar"].sort_values(
    "rover_screening_score_100", ascending=False
).head(25)

polar = polar.copy()
nonpolar = nonpolar.copy()
polar.insert(0, "group_rank", range(1, len(polar) + 1))
nonpolar.insert(0, "group_rank", range(1, len(nonpolar) + 1))

columns = [
    "group_rank", "tile", "rover_screening_score_100",
    "latitude", "longitude", "p90_slope_degrees",
    "p90_roughness_630m_m", "local_relief_630m_p90_m",
    "lower_relief_screen_percent", "challenging_terrain_percent"
]
columns = [c for c in columns if c in df.columns]

polar_path = folder / "top25_polar_candidates.csv"
nonpolar_path = folder / "top25_nonpolar_candidates.csv"
combined_path = folder / "geographic_candidate_shortlist.csv"

polar[columns].to_csv(polar_path, index=False, float_format="%.4f")
nonpolar[columns].to_csv(nonpolar_path, index=False, float_format="%.4f")

combined = pd.concat([
    polar.assign(geographic_group="Polar"),
    nonpolar.assign(geographic_group="Non-polar")
])
combined[["geographic_group"] + columns].to_csv(
    combined_path, index=False, float_format="%.4f"
)

# Global map of all ranked tiles, highlighting the two shortlisted groups.
fig, ax = plt.subplots(figsize=(14, 8))
ax.scatter(
    df["longitude"], df["latitude"],
    c="lightgray", s=10, alpha=0.45, label="Other ranked tiles"
)
ax.scatter(
    nonpolar["longitude"], nonpolar["latitude"],
    c="green", s=35, label="Top 25 non-polar"
)
ax.scatter(
    polar["longitude"], polar["latitude"],
    c="royalblue", s=35, label="Top 25 polar"
)
ax.axhline(60, color="royalblue", linestyle="--", linewidth=0.8)
ax.axhline(-60, color="royalblue", linestyle="--", linewidth=0.8)
ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Geographic Shortlist of Rover-Terrain Candidates")
ax.grid(alpha=0.2)
ax.legend(loc="lower left")
fig.tight_layout()

map_path = folder / "geographic_candidate_shortlist_map.png"
fig.savefig(map_path, dpi=220)
plt.close(fig)

report_path = folder / "GEOGRAPHIC_CANDIDATE_SHORTLIST.md"
with report_path.open("w", encoding="utf-8") as f:
    f.write("# Geographic Candidate Shortlist\n\n")
    f.write(f"- Ranked tiles with coordinates: **{len(df)}**\n")
    f.write(f"- Polar tiles (|latitude| >= 60°): **{(df['geographic_group'] == 'Polar').sum()}**\n")
    f.write(f"- Non-polar tiles: **{(df['geographic_group'] == 'Non-polar').sum()}**\n")
    f.write("- Shortlist rule: top 25 by terrain score in each group, or all available if fewer than 25.\n")
    f.write("- This is geographic screening only. Polar conditions, climate, surface material, "
            "imagery, hazards and mission engineering constraints are not evaluated here.\n\n")
    f.write("## Top non-polar candidates\n\n")
    f.write(nonpolar[columns].to_string(index=False))
    f.write("\n\n## Top polar candidates\n\n")
    f.write(polar[columns].to_string(index=False))
    f.write("\n")

print("\n=== GEOGRAPHIC SHORTLIST COMPLETE ===")
print("Tiles with coordinates:", len(df))
print("Polar tiles:", (df["geographic_group"] == "Polar").sum())
print("Non-polar tiles:", (df["geographic_group"] == "Non-polar").sum())

print("\nTOP 10 NON-POLAR:")
print(nonpolar[["group_rank", "tile", "rover_screening_score_100",
                "latitude", "longitude"]].head(10).to_string(index=False))

print("\nTOP 10 POLAR:")
print(polar[["group_rank", "tile", "rover_screening_score_100",
             "latitude", "longitude"]].head(10).to_string(index=False))

print("\nCSV:", combined_path)
print("MAP:", map_path)
print("REPORT:", report_path)
