from pathlib import Path
import csv
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SOURCE = Path("data/processed/global_terrain/advanced_rasters")
OUTPUT = Path("data/processed/global_terrain/rover_screening")
RASTER_OUT = OUTPUT / "screening_rasters"
SUMMARY = OUTPUT / "global_rover_screening_summary.csv"
MAP = OUTPUT / "global_rover_screening_map.png"

# Provisional exploratory screening thresholds.
LOW_SLOPE = 5.0
LOW_ROUGHNESS = 2.0
MID_SLOPE = 15.0
MID_ROUGHNESS = 5.0

def main():
    files = sorted(SOURCE.glob("*.tif"))
    if not files:
        raise FileNotFoundError(f"No input rasters found: {SOURCE}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    RASTER_OUT.mkdir(parents=True, exist_ok=True)

    rows = []
    map_items = []
    failures = []

    for number, path in enumerate(files, 1):
        try:
            with rasterio.open(path) as src:
                if src.count < 3:
                    raise ValueError("Expected at least 3 bands")

                slope = src.read(1).astype(np.float32)
                roughness = src.read(3).astype(np.float32)

                valid = (
                    np.isfinite(slope)
                    & np.isfinite(roughness)
                    & (slope != src.nodata)
                    & (roughness != src.nodata)
                    & (slope >= 0)
                    & (roughness >= 0)
                )

                if not valid.any():
                    raise ValueError("No valid slope/roughness pixels")

                # 1 = lower-relief screen, 2 = intermediate,
                # 3 = more challenging, 0 = nodata.
                classes = np.zeros(slope.shape, dtype=np.uint8)

                lower = (
                    valid
                    & (slope <= LOW_SLOPE)
                    & (roughness <= LOW_ROUGHNESS)
                )

                intermediate = (
                    valid
                    & ~lower
                    & (slope <= MID_SLOPE)
                    & (roughness <= MID_ROUGHNESS)
                )

                challenging = valid & ~lower & ~intermediate

                classes[lower] = 1
                classes[intermediate] = 2
                classes[challenging] = 3

                profile = src.profile.copy()
                profile.update(
                    count=1,
                    dtype="uint8",
                    nodata=0,
                    compress="deflate"
                )

                out_path = RASTER_OUT / (
                    path.stem.replace("_advanced_terrain", "")
                    + "_rover_screening.tif"
                )

                with rasterio.open(out_path, "w", **profile) as dst:
                    dst.write(classes, 1)
                    dst.set_band_description(
                        1, "Provisional rover terrain screening class"
                    )

                count = int(valid.sum())
                lower_pct = 100 * int(lower.sum()) / count
                intermediate_pct = 100 * int(intermediate.sum()) / count
                challenging_pct = 100 * int(challenging.sum()) / count

                bounds = src.bounds

                rows.append({
                    "tile": path.stem,
                    "valid_pixels": count,
                    "mean_slope_degrees": float(np.mean(slope[valid])),
                    "p90_slope_degrees": float(np.percentile(slope[valid], 90)),
                    "mean_roughness_630m_m": float(np.mean(roughness[valid])),
                    "p90_roughness_630m_m": float(
                        np.percentile(roughness[valid], 90)
                    ),
                    "lower_relief_screen_percent": lower_pct,
                    "intermediate_screen_percent": intermediate_pct,
                    "challenging_terrain_percent": challenging_pct,
                    "screening_raster": str(out_path)
                })

                map_items.append((
                    bounds.left, bounds.bottom,
                    bounds.right - bounds.left,
                    bounds.top - bounds.bottom,
                    lower_pct
                ))

            if number % 25 == 0 or number == len(files):
                print(f"Processed {number}/{len(files)}")

        except Exception as exc:
            failures.append((path.name, str(exc)))
            print(f"FAILED: {path.name}: {exc}")

    if rows:
        with SUMMARY.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        fig, ax = plt.subplots(figsize=(16, 8))

        for x, y, width, height, value in map_items:
            ax.add_patch(Rectangle(
                (x, y), width, height,
                facecolor=plt.cm.viridis(value / 100),
                edgecolor="none"
            ))

        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title(
            "Global Preliminary Rover Terrain Screening\n"
            "Tile colour = percentage meeting lower-relief screening criteria"
        )
        ax.grid(alpha=0.2)

        scalar = plt.cm.ScalarMappable(
            cmap="viridis",
            norm=plt.Normalize(0, 100)
        )
        scalar.set_array([])
        fig.colorbar(
            scalar, ax=ax,
            label="Lower-relief screening pixels (%)"
        )

        fig.tight_layout()
        fig.savefig(MAP, dpi=200)
        plt.close(fig)

    print("\n=== ROVER SCREENING COMPLETE ===")
    print("Input rasters:", len(files))
    print("Successful:", len(rows))
    print("Failed:", len(failures))
    print("Summary:", SUMMARY)
    print("Map:", MAP)
    print("Screening rasters:", RASTER_OUT)

    if failures:
        failure_file = OUTPUT / "screening_failures.csv"
        with failure_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "error"])
            writer.writerows(failures)
        print("Failure details:", failure_file)

if __name__ == "__main__":
    main()
