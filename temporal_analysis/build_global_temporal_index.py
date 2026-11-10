from pathlib import Path
import csv
import rasterio
from rasterio.warp import transform_bounds
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SOURCE = Path("data/processed/global_terrain/advanced_rasters")
OUT = Path("data/processed/temporal_analysis/global")
OUT.mkdir(parents=True, exist_ok=True)

rasters = sorted(SOURCE.glob("*.tif"))

if not rasters:
    raise SystemExit(f"No rasters found in {SOURCE}")

records = []

for i, path in enumerate(rasters, 1):
    try:
        with rasterio.open(path) as ds:
            bounds = transform_bounds(
                ds.crs, "EPSG:4326", *ds.bounds, densify_pts=11
            )
            west, south, east, north = bounds

            records.append({
                "tile": path.stem,
                "raster": str(path),
                "west": west,
                "south": south,
                "east": east,
                "north": north,
                "center_lon": (west + east) / 2,
                "center_lat": (south + north) / 2,
                "width": ds.width,
                "height": ds.height,
            })
    except Exception as exc:
        print("FAILED:", path.name, exc)

    if i % 100 == 0:
        print(f"Indexed {i}/{len(rasters)}")

csv_path = OUT / "global_temporal_targets.csv"

with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

fig, ax = plt.subplots(figsize=(16, 8))

for r in records:
    ax.plot(
        [r["west"], r["east"], r["east"], r["west"], r["west"]],
        [r["south"], r["south"], r["north"], r["north"], r["south"]],
        linewidth=0.25
    )

ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(
    f"TERRATIME4D - Global temporal analysis target inventory "
    f"({len(records)} DEM tiles)"
)
ax.grid(alpha=0.2)

fig.savefig(OUT / "global_temporal_coverage.png",
            dpi=200, bbox_inches="tight")
plt.close(fig)

print("\nGLOBAL INDEX COMPLETE")
print("Indexed tiles:", len(records))
print("CSV:", csv_path)
print("Map:", OUT / "global_temporal_coverage.png")
