from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import time

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform
import matplotlib.pyplot as plt

BASE = Path("data/processed/temporal_analysis/global")
SOURCE = BASE / "global_mgrs_quarterly_index.csv"
OUT = BASE / "global_scene_metrics.csv"
ERRORS = BASE / "global_scene_errors.csv"
CHANGES = BASE / "global_quarterly_change_metrics.csv"
MAP = BASE / "global_quarterly_ndvi_change.png"

SIZE = 256
WORKERS = 4
SAVE_EVERY = 100

df = pd.read_csv(SOURCE, low_memory=False)
df = df.dropna(subset=["red_href", "nir_href", "scl_href"]).copy()

# Resume from previously completed records.
done = set()
if OUT.exists():
    try:
        old = pd.read_csv(OUT, usecols=["record_key"])
        done = set(old["record_key"].astype(str))
    except Exception:
        pass

df["record_key"] = (
    df["mgrs_tile"].astype(str) + "|" + df["scene_id"].astype(str)
)
df = df[~df["record_key"].isin(done)]

print("GLOBAL QUARTERLY IMAGE ANALYSIS")
print("Records already completed:", len(done))
print("Records remaining:", len(df))
print("Workers:", WORKERS)
print("Resolution per scene:", SIZE, "x", SIZE)

def process(row):
    import rasterio

    result = {
        "record_key": row.record_key,
        "scene_id": row.scene_id,
        "mgrs_tile": row.mgrs_tile,
        "year": int(row.year),
        "quarter": int(row.quarter),
        "acquisition_date": row.acquisition_date,
    }

    try:
        with rasterio.Env(
            GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
            CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
            GDAL_HTTP_MULTIRANGE="YES",
            GDAL_NUM_THREADS="1",
        ):
            with rasterio.open(row.red_href) as red_src:
                red = red_src.read(
                    1, out_shape=(SIZE, SIZE),
                    resampling=Resampling.bilinear
                ).astype("float32")

                bounds = red_src.bounds
                cx = (bounds.left + bounds.right) / 2
                cy = (bounds.bottom + bounds.top) / 2
                lon, lat = transform(
                    red_src.crs, "EPSG:4326", [cx], [cy]
                )

            with rasterio.open(row.nir_href) as nir_src:
                nir = nir_src.read(
                    1, out_shape=(SIZE, SIZE),
                    resampling=Resampling.bilinear
                ).astype("float32")

            with rasterio.open(row.scl_href) as scl_src:
                scl = scl_src.read(
                    1, out_shape=(SIZE, SIZE),
                    resampling=Resampling.nearest
                )

        # Sentinel-2 SCL: 4 vegetation, 5 bare soil, 6 water.
        vegetation = scl == 4
        bare = scl == 5
        water = scl == 6
        valid = vegetation | bare | water
        land = vegetation | bare

        denominator = nir + red
        usable = land & np.isfinite(denominator) & (denominator > 0)

        ndvi = np.full(red.shape, np.nan, dtype="float32")
        ndvi[usable] = (
            (nir[usable] - red[usable]) /
            denominator[usable]
        )

        result.update({
            "longitude": lon[0],
            "latitude": lat[0],
            "valid_pixel_fraction": float(valid.mean()),
            "vegetation_fraction": float(
                vegetation.sum() / max(valid.sum(), 1)
            ),
            "bare_soil_fraction": float(
                bare.sum() / max(valid.sum(), 1)
            ),
            "scl_water_fraction": float(
                water.sum() / max(valid.sum(), 1)
            ),
            "mean_ndvi": (
                float(np.nanmean(ndvi)) if np.isfinite(ndvi).any()
                else np.nan
            ),
            "median_ndvi": (
                float(np.nanmedian(ndvi)) if np.isfinite(ndvi).any()
                else np.nan
            ),
            "status": "SUCCESS",
        })

    except Exception as exc:
        result.update({
            "status": "FAILED",
            "error": str(exc)[:500],
        })

    return result


records = df.itertuples(index=False)
pending = []
completed = 0
success = 0
failed = 0

fieldnames = [
    "record_key", "scene_id", "mgrs_tile", "year", "quarter",
    "acquisition_date", "longitude", "latitude",
    "valid_pixel_fraction", "vegetation_fraction",
    "bare_soil_fraction", "scl_water_fraction",
    "mean_ndvi", "median_ndvi", "status", "error"
]

out_exists = OUT.exists()
err_exists = ERRORS.exists()

with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(process, row): row.scene_id for row in records}

    with OUT.open("a", newline="", encoding="utf-8") as out_file, \
         ERRORS.open("a", newline="", encoding="utf-8") as err_file:

        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        error_writer = csv.DictWriter(
            err_file,
            fieldnames=["record_key", "scene_id", "mgrs_tile",
                        "year", "quarter", "status", "error"]
        )

        if not out_exists:
            writer.writeheader()
        if not err_exists:
            error_writer.writeheader()

        for future in as_completed(futures):
            result = future.result()
            pending.append(result)
            completed += 1

            if result["status"] == "SUCCESS":
                success += 1
            else:
                failed += 1

            if len(pending) >= SAVE_EVERY:
                for item in pending:
                    writer.writerow(item)
                    if item["status"] == "FAILED":
                        error_writer.writerow(item)
                out_file.flush()
                err_file.flush()
                pending.clear()

            if completed % 100 == 0:
                print(
                    f"Processed {completed}/{len(df)} | "
                    f"Success: {success} | Failed: {failed}",
                    flush=True
                )

        for item in pending:
            writer.writerow(item)
            if item["status"] == "FAILED":
                error_writer.writerow(item)

        out_file.flush()
        err_file.flush()

print("\nIMAGE PROCESSING FINISHED")
print("New successful scenes:", success)
print("New failed scenes:", failed)
print("Scene metrics:", OUT)
print("Error log:", ERRORS)

# Build temporal comparisons from all successful saved records.
metrics = pd.read_csv(OUT)
metrics = metrics[metrics["status"] == "SUCCESS"].copy()

for col in ["year", "quarter", "mean_ndvi",
            "bare_soil_fraction", "scl_water_fraction"]:
    metrics[col] = pd.to_numeric(metrics[col], errors="coerce")

metrics = metrics.dropna(
    subset=["year", "quarter", "mean_ndvi"]
)

metrics = metrics.sort_values(
    ["mgrs_tile", "quarter", "year"]
)

groups = metrics.groupby(["mgrs_tile", "quarter"])

metrics["previous_year"] = groups["year"].shift(1)
for col in ["mean_ndvi", "bare_soil_fraction",
            "scl_water_fraction"]:
    metrics[f"{col}_change"] = groups[col].diff()

changes = metrics.dropna(subset=["previous_year"]).copy()
changes.to_csv(CHANGES, index=False)

print("\nTEMPORAL COMPARISON")
print("Successful scene records:", len(metrics))
print("Tile-quarter comparisons:", len(changes))
print("Saved:", CHANGES)

# Latest available comparison per tile for a global overview map.
if not changes.empty:
    latest = (
        changes.sort_values(["year", "quarter"])
        .groupby("mgrs_tile")
        .tail(1)
    )

    plt.figure(figsize=(16, 8))
    scatter = plt.scatter(
        latest["longitude"],
        latest["latitude"],
        c=latest["mean_ndvi_change"],
        cmap="RdYlBu",
        s=5,
        vmin=-0.5,
        vmax=0.5
    )
    plt.colorbar(scatter, label="NDVI change")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Global Sentinel-2 Quarterly NDVI Change")
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(MAP, dpi=200)
    plt.close()
    print("Global map:", MAP)

print("\nPIPELINE COMPLETE")
