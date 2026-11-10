from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
from rasterio.warp import transform

BASE = Path("data/processed/temporal_analysis/global")
SOURCE = BASE / "global_mgrs_quarterly_index.csv"
MANIFEST = BASE / "global_tile_change_pairs.csv"
OUT = BASE / "global_tile_change_metrics_fast.csv"
ERRORS = BASE / "global_tile_change_errors_fast.csv"

NDVI_MAP = BASE / "global_ndvi_change_map.png"
BARE_MAP = BASE / "global_bare_soil_change_map.png"

SIZE = 128
WORKERS = 4

# -------------------------------------------------
# 1. Select one earliest/latest same-quarter pair
#    per MGRS tile, requiring at least one year gap.
# -------------------------------------------------
df = pd.read_csv(SOURCE, low_memory=False)

df["acquisition_date"] = pd.to_datetime(
    df["acquisition_date"], errors="coerce"
)
df["cloud_cover"] = pd.to_numeric(
    df["cloud_cover"], errors="coerce"
)

df = df.dropna(subset=[
    "mgrs_tile", "acquisition_date",
    "red_href", "nir_href", "scl_href"
]).copy()

df = df.drop_duplicates(["mgrs_tile", "scene_id"])

candidates = []

for (tile, quarter), group in df.groupby(
    ["mgrs_tile", "quarter"]
):
    group = group.sort_values("acquisition_date")
    first = group.iloc[0]
    last = group.iloc[-1]

    if first["scene_id"] == last["scene_id"]:
        continue

    gap = (last["acquisition_date"] -
           first["acquisition_date"]).days

    if gap < 365:
        continue

    candidates.append({
        "mgrs_tile": tile,
        "quarter": int(quarter),
        "first": first,
        "last": last,
        "gap_days": gap,
        "mean_cloud": np.nanmean([
            first["cloud_cover"], last["cloud_cover"]
        ])
    })

# Choose the longest time gap for each tile.
# For equal gaps, prefer the lower-cloud pair.
chosen = {}
for item in candidates:
    tile = item["mgrs_tile"]
    score = (item["gap_days"], -(
        item["mean_cloud"]
        if np.isfinite(item["mean_cloud"]) else 100
    ))
    if tile not in chosen or score > chosen[tile][0]:
        chosen[tile] = (score, item)

pairs = []
for tile, (_, item) in chosen.items():
    a, b = item["first"], item["last"]
    pairs.append({
        "pair_id": tile,
        "mgrs_tile": tile,
        "quarter": item["quarter"],
        "gap_days": item["gap_days"],
        "first_scene": a["scene_id"],
        "first_date": str(a["acquisition_date"].date()),
        "first_red": a["red_href"],
        "first_nir": a["nir_href"],
        "first_scl": a["scl_href"],
        "last_scene": b["scene_id"],
        "last_date": str(b["acquisition_date"].date()),
        "last_red": b["red_href"],
        "last_nir": b["nir_href"],
        "last_scl": b["scl_href"],
    })

manifest = pd.DataFrame(pairs)
manifest.to_csv(MANIFEST, index=False)

print("GLOBAL BEFORE/AFTER PAIRS")
print("Tiles with usable pairs:", len(manifest))
print("Tiles without qualifying pairs:",
      df["mgrs_tile"].nunique() - len(manifest))
print("Pair manifest:", MANIFEST)

# -------------------------------------------------
# 2. Read a scene's three bands and calculate metrics
# -------------------------------------------------
def read_scene(red_url, nir_url, scl_url):
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
        GDAL_HTTP_TIMEOUT="25",
        GDAL_HTTP_MAX_RETRY="1",
        GDAL_NUM_THREADS="1"
    ):
        with rasterio.open(red_url) as src:
            red = src.read(
                1, out_shape=(SIZE, SIZE),
                resampling=Resampling.bilinear
            ).astype("float32")
            bounds = src.bounds
            lon, lat = transform(
                src.crs, "EPSG:4326",
                [(bounds.left + bounds.right) / 2],
                [(bounds.bottom + bounds.top) / 2]
            )

        with rasterio.open(nir_url) as src:
            nir = src.read(
                1, out_shape=(SIZE, SIZE),
                resampling=Resampling.bilinear
            ).astype("float32")

        with rasterio.open(scl_url) as src:
            scl = src.read(
                1, out_shape=(SIZE, SIZE),
                resampling=Resampling.nearest
            )

    vegetation = scl == 4
    bare = scl == 5
    water = scl == 6
    valid = vegetation | bare | water
    land = vegetation | bare

    usable = land & (red > 0) & (nir > 0)
    denominator = red + nir

    ndvi = np.full(red.shape, np.nan, dtype="float32")
    usable &= denominator > 0
    ndvi[usable] = (
        (nir[usable] - red[usable]) / denominator[usable]
    )

    land_count = max(int(land.sum()), 1)
    valid_count = max(int(valid.sum()), 1)

    return {
        "longitude": lon[0],
        "latitude": lat[0],
        "mean_ndvi": (
            float(np.nanmean(ndvi))
            if np.isfinite(ndvi).any() else np.nan
        ),
        "vegetation_fraction": float(
            vegetation.sum() / land_count
        ),
        "bare_soil_fraction": float(
            bare.sum() / land_count
        ),
        "scl_water_fraction": float(
            water.sum() / valid_count
        ),
        "valid_pixel_fraction": float(valid.mean())
    }

# -------------------------------------------------
# 3. Process pairs, resume completed successes
# -------------------------------------------------
fields = [
    "pair_id", "mgrs_tile", "quarter",
    "first_scene", "first_date",
    "last_scene", "last_date", "gap_days",
    "longitude", "latitude",
    "first_mean_ndvi", "last_mean_ndvi", "ndvi_change",
    "first_vegetation_fraction", "last_vegetation_fraction",
    "vegetation_fraction_change",
    "first_bare_soil_fraction", "last_bare_soil_fraction",
    "bare_soil_fraction_change",
    "first_water_fraction", "last_water_fraction",
    "water_fraction_change",
    "first_valid_fraction", "last_valid_fraction"
]

done = set()
if OUT.exists():
    previous = pd.read_csv(OUT, usecols=["pair_id"])
    done = set(previous["pair_id"].astype(str))

pending = manifest[
    ~manifest["pair_id"].astype(str).isin(done)
].copy()

print("\nAlready completed:", len(done))
print("Pairs remaining:", len(pending))
print("Workers:", WORKERS)
print("Sampling size:", SIZE, "x", SIZE)

def process_pair(row):
    result = {
        "pair_id": row.pair_id,
        "mgrs_tile": row.mgrs_tile,
        "quarter": row.quarter,
        "first_scene": row.first_scene,
        "first_date": row.first_date,
        "last_scene": row.last_scene,
        "last_date": row.last_date,
        "gap_days": row.gap_days
    }

    try:
        first = read_scene(
            row.first_red, row.first_nir, row.first_scl
        )
        last = read_scene(
            row.last_red, row.last_nir, row.last_scl
        )

        result.update({
            "longitude": first["longitude"],
            "latitude": first["latitude"],
            "first_mean_ndvi": first["mean_ndvi"],
            "last_mean_ndvi": last["mean_ndvi"],
            "ndvi_change": (
                last["mean_ndvi"] - first["mean_ndvi"]
            ),
            "first_vegetation_fraction":
                first["vegetation_fraction"],
            "last_vegetation_fraction":
                last["vegetation_fraction"],
            "vegetation_fraction_change": (
                last["vegetation_fraction"] -
                first["vegetation_fraction"]
            ),
            "first_bare_soil_fraction":
                first["bare_soil_fraction"],
            "last_bare_soil_fraction":
                last["bare_soil_fraction"],
            "bare_soil_fraction_change": (
                last["bare_soil_fraction"] -
                first["bare_soil_fraction"]
            ),
            "first_water_fraction": first["scl_water_fraction"],
            "last_water_fraction": last["scl_water_fraction"],
            "water_fraction_change": (
                last["scl_water_fraction"] -
                first["scl_water_fraction"]
            ),
            "first_valid_fraction":
                first["valid_pixel_fraction"],
            "last_valid_fraction":
                last["valid_pixel_fraction"]
        })
        return result, None

    except Exception as exc:
        return None, {
            "pair_id": row.pair_id,
            "mgrs_tile": row.mgrs_tile,
            "first_scene": row.first_scene,
            "last_scene": row.last_scene,
            "error": str(exc)[:500]
        }

out_exists = OUT.exists()
err_exists = ERRORS.exists()

completed = 0
failed = 0

with OUT.open("a", newline="", encoding="utf-8") as out_file, \
     ERRORS.open("a", newline="", encoding="utf-8") as err_file:

    writer = csv.DictWriter(out_file, fieldnames=fields)
    error_writer = csv.DictWriter(
        err_file,
        fieldnames=[
            "pair_id", "mgrs_tile", "first_scene",
            "last_scene", "error"
        ]
    )

    if not out_exists:
        writer.writeheader()
    if not err_exists:
        error_writer.writeheader()

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [
            pool.submit(process_pair, row)
            for row in pending.itertuples(index=False)
        ]

        for future in as_completed(futures):
            result, error = future.result()
            completed += 1

            if result is not None:
                writer.writerow(result)
                out_file.flush()
            else:
                failed += 1
                error_writer.writerow(error)
                err_file.flush()

            if completed % 25 == 0:
                print(
                    f"Processed {completed}/{len(pending)} "
                    f"| New failures: {failed}",
                    flush=True
                )

print("\nPAIR PROCESSING FINISHED")
print("New successful pairs:", completed - failed)
print("New failed pairs:", failed)
print("Metrics:", OUT)
print("Errors:", ERRORS)

# -------------------------------------------------
# 4. Generate global maps from successful comparisons
# -------------------------------------------------
if OUT.exists():
    result = pd.read_csv(OUT)
    if not result.empty:
        for col in [
            "ndvi_change", "bare_soil_fraction_change",
            "vegetation_fraction_change"
        ]:
            result[col] = pd.to_numeric(
                result[col], errors="coerce"
            )

        result = result.dropna(
            subset=["longitude", "latitude", "ndvi_change"]
        )

        def make_map(column, filename, title, label):
            plt.figure(figsize=(16, 8))
            points = plt.scatter(
                result["longitude"],
                result["latitude"],
                c=result[column],
                cmap="RdYlBu",
                s=6
            )
            plt.colorbar(points, label=label)
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.title(title)
            plt.xlim(-180, 180)
            plt.ylim(-90, 90)
            plt.grid(alpha=0.2)
            plt.tight_layout()
            plt.savefig(filename, dpi=200)
            plt.close()
            print("Map saved:", filename)

        make_map(
            "ndvi_change", NDVI_MAP,
            "Global Same-Quarter NDVI Change",
            "NDVI change"
        )
        make_map(
            "bare_soil_fraction_change", BARE_MAP,
            "Global Same-Quarter Bare-Soil Fraction Change",
            "Fraction change"
        )

        print("\nSUCCESSFUL TILE COMPARISONS:", len(result))

print("\nPIPELINE FINISHED")
