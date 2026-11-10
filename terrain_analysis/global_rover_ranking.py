from pathlib import Path
import re
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform_bounds
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path("data/processed/global_terrain")
raster_dir = root / "advanced_rasters"
out = root / "rover_screening"
source = out / "global_rover_screening_summary.csv"

def tile_key(value):
    name = Path(str(value)).stem
    name = re.sub(r"_advanced_terrain$", "", name, flags=re.I)
    return name.casefold()

rover = pd.read_csv(source)
rover["_key"] = rover["tile"].map(tile_key)

records = []
rasters = sorted(raster_dir.glob("*_advanced_terrain.tif"))

for i, path in enumerate(rasters, 1):
    with rasterio.open(path) as ds:
        if ds.count < 10:
            raise SystemExit(f"Expected 10 bands, found {ds.count}: {path.name}")
        relief = ds.read(6, masked=True).compressed()
        relief = relief[np.isfinite(relief)]
        relief_p90 = float(np.percentile(relief, 90)) if relief.size else np.nan

        if ds.crs:
            west, south, east, north = transform_bounds(
                ds.crs, "EPSG:4326", *ds.bounds
            )
            lon = (west + east) / 2
            lat = (south + north) / 2
        else:
            lon = lat = np.nan

    records.append({
        "_key": tile_key(path.name),
        "local_relief_630m_p90_m": relief_p90,
        "longitude": lon,
        "latitude": lat
    })

    if i % 100 == 0:
        print(f"Read relief statistics: {i}/{len(rasters)}")

relief = pd.DataFrame(records)
df = rover.merge(relief, on="_key", how="inner", validate="one_to_one")

if len(df) != len(rasters) or len(df) != len(rover):
    raise SystemExit(
        f"Tile matching issue: rasters={len(rasters)}, "
        f"screening rows={len(rover)}, matched={len(df)}. "
        "Stopped without producing a ranking."
    )

inputs = [
    "p90_slope_degrees",
    "p90_roughness_630m_m",
    "local_relief_630m_p90_m",
    "lower_relief_screen_percent"
]

for col in inputs:
    if col not in df.columns:
        raise SystemExit(f"Required column missing: {col}")
    df[col] = pd.to_numeric(df[col], errors="coerce")

if df[inputs].isna().any().any():
    raise SystemExit("Missing ranking values detected. No ranking written.")

# Convert each measure to a relative percentile score.
# Lower slope, roughness and relief are preferred.
df["slope_score"] = 1 - df["p90_slope_degrees"].rank(pct=True)
df["roughness_score"] = 1 - df["p90_roughness_630m_m"].rank(pct=True)
df["relief_score"] = 1 - df["local_relief_630m_p90_m"].rank(pct=True)
df["lower_relief_score"] = df["lower_relief_screen_percent"].rank(pct=True)

df["rover_screening_score_100"] = 100 * (
    0.35 * df["slope_score"]
    + 0.25 * df["roughness_score"]
    + 0.20 * df["relief_score"]
    + 0.20 * df["lower_relief_score"]
)

df = df.sort_values(
    "rover_screening_score_100", ascending=False
).reset_index(drop=True)

df.insert(0, "rank", np.arange(1, len(df) + 1))

columns = [
    "rank", "tile", "rover_screening_score_100",
    "p90_slope_degrees", "p90_roughness_630m_m",
    "local_relief_630m_p90_m", "lower_relief_screen_percent",
    "mean_slope_degrees", "mean_roughness_630m_m",
    "challenging_terrain_percent", "longitude", "latitude"
]
columns = [c for c in columns if c in df.columns]

csv_path = out / "global_rover_terrain_ranking.csv"
df[columns].to_csv(csv_path, index=False, float_format="%.4f")

# Global map: all ranked tile centres, with top 20 outlined.
valid = df[np.isfinite(df["longitude"]) & np.isfinite(df["latitude"])]
top = df.head(20)

fig, ax = plt.subplots(figsize=(14, 8))
points = ax.scatter(
    valid["longitude"], valid["latitude"],
    c=valid["rover_screening_score_100"],
    cmap="viridis", vmin=0, vmax=100, s=17, alpha=0.85
)
ax.scatter(
    top["longitude"], top["latitude"],
    facecolors="none", edgecolors="red",
    s=45, linewidths=0.9, label="Top 20 ranked tiles"
)
ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Global Rover-Terrain Screening Ranking")
ax.grid(alpha=0.2)
ax.legend(loc="lower left")
fig.colorbar(points, ax=ax, label="Relative screening score (0–100)")
fig.tight_layout()

map_path = out / "global_rover_terrain_ranking_map.png"
fig.savefig(map_path, dpi=220)
plt.close(fig)

report_path = out / "GLOBAL_ROVER_TERRAIN_RANKING.md"
with report_path.open("w", encoding="utf-8") as f:
    f.write("# Global Rover-Terrain Screening Ranking\n\n")
    f.write(f"Tiles ranked: **{len(df)}**\n\n")
    f.write("Weights: slope 35%, 630 m roughness 25%, "
            "630 m local relief 20%, lower-relief share 20%.\n\n")
    f.write("Scores are relative screening scores, not probabilities "
            "or certified landing-safety ratings. Copernicus GLO-90 is a "
            "digital surface model; vegetation, buildings and data quality "
            "can affect results. Mission-specific engineering assessment "
            "and higher-resolution data are still required.\n\n")
    f.write("## Top 20 tiles\n\n")
    f.write(top[columns].to_string(index=False))
    f.write("\n")

print("\n=== GLOBAL ROVER RANKING COMPLETE ===")
print("Tiles ranked:", len(df))
print("\nTOP 10:")
print(df[["rank", "tile", "rover_screening_score_100"]].head(10).to_string(index=False))
print("\nCSV:", csv_path)
print("MAP:", map_path)
print("REPORT:", report_path)
