from pathlib import Path
from collections import defaultdict
import argparse
import csv
import shutil
import tempfile
import zipfile

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import uniform_filter


PROJECT = Path(__file__).resolve().parents[1]
ARCHIVE_FOLDER = PROJECT.parent

ARCHIVES = sorted(
    ARCHIVE_FOLDER.glob("TERRATIME4D_DEM*.zip")
)

GLOBAL_ROOT = PROJECT / "data" / "processed" / "global_terrain"

ADVANCED_FOLDER = GLOBAL_ROOT / "advanced_rasters"
CLASSIFICATION_FOLDER = GLOBAL_ROOT / "classification_rasters"

SUMMARY_FILE = GLOBAL_ROOT / "global_terrain_classification_summary.csv"
LOG_FILE = GLOBAL_ROOT / "global_classification_processing_log.csv"

TPI_SCALE_M = 1000.0
MIN_VALID_FRACTION = 0.75
NODATA_CLASS = 0

CLASS_NAMES = {
    1: "flat_smooth",
    2: "rolling",
    3: "rugged",
    4: "relative_ridge",
    5: "relative_valley",
}


def build_inventory():
    inventory = defaultdict(list)

    for archive in ARCHIVES:
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue

                if not info.filename.lower().endswith((".tif", ".tiff")):
                    continue

                inventory[Path(info.filename).name.lower()].append(
                    (archive, info)
                )

    selected = []
    conflicts = []

    for filename, entries in sorted(inventory.items()):
        signatures = {
            (info.CRC, info.file_size)
            for _, info in entries
        }

        if len(signatures) > 1:
            conflicts.append(filename)
            continue

        selected.append((filename, entries[0][0], entries[0][1]))

    return selected, conflicts


def odd_window(distance_m, pixel_m):
    pixels = max(3, int(round(distance_m / pixel_m)))

    if pixels % 2 == 0:
        pixels += 1

    return pixels


def calculate_tpi(elevation, valid_mask, window):
    valid_float = valid_mask.astype(np.float32)

    numerator = uniform_filter(
        np.where(valid_mask, elevation, 0).astype(np.float32),
        size=window,
        mode="constant",
        cval=0
    )

    denominator = uniform_filter(
        valid_float,
        size=window,
        mode="constant",
        cval=0
    )

    local_mean = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator > 0
    )

    tpi = elevation - local_mean

    tpi_valid = (
        valid_mask &
        (denominator >= MIN_VALID_FRACTION)
    )

    return tpi, tpi_valid


def get_advanced_bands(dataset):
    descriptions = {
        (description or "").strip().lower(): index
        for index, description in enumerate(dataset.descriptions, start=1)
    }

    slope_band = descriptions.get("slope_degrees", 1)
    roughness_band = descriptions.get("roughness_630m", 3)

    slope = dataset.read(slope_band).astype(np.float32)
    roughness = dataset.read(roughness_band).astype(np.float32)

    return slope, roughness


def classify_tile(dem_path, filename):
    stem = Path(filename).stem

    advanced_path = (
        ADVANCED_FOLDER /
        f"{stem}_advanced_terrain.tif"
    )

    if not advanced_path.exists():
        raise FileNotFoundError(
            f"Matching advanced raster not found: {advanced_path.name}"
        )

    with rasterio.open(dem_path) as dem:
        elevation = dem.read(1).astype(np.float32)
        dem_profile = dem.profile.copy()
        dem_transform = dem.transform
        dem_crs = dem.crs
        dem_shape = dem.shape
        nodata = dem.nodata

    valid = np.isfinite(elevation)

    if nodata is not None:
        valid &= elevation != nodata

    if not valid.any():
        raise ValueError("No valid elevation pixels")

    with rasterio.open(advanced_path) as advanced:
        if (
            advanced.shape != dem_shape
            or advanced.transform != dem_transform
            or advanced.crs != dem_crs
        ):
            raise ValueError(
                "DEM and advanced raster grids do not match"
            )

        slope, roughness = get_advanced_bands(advanced)

    latitude = dem_transform.f + (
        dem_shape[0] * dem_transform.e / 2
    )

    pixel_width_m = max(
        0.1,
        abs(dem_transform.a) *
        111320 *
        max(0.01, abs(np.cos(np.radians(latitude))))
    )

    pixel_height_m = max(
        0.1,
        abs(dem_transform.e) * 111320
    )

    window_x = odd_window(TPI_SCALE_M, pixel_width_m)
    window_y = odd_window(TPI_SCALE_M, pixel_height_m)

    # Use a rectangular window to account approximately
    # for the different ground dimensions of x and y pixels.
    valid_float = valid.astype(np.float32)

    numerator = uniform_filter(
        np.where(valid, elevation, 0).astype(np.float32),
        size=(window_y, window_x),
        mode="constant",
        cval=0
    )

    denominator = uniform_filter(
        valid_float,
        size=(window_y, window_x),
        mode="constant",
        cval=0
    )

    local_mean = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator > 0
    )

    tpi = elevation - local_mean

    analysis_valid = (
        valid &
        (denominator >= MIN_VALID_FRACTION) &
        np.isfinite(slope) &
        np.isfinite(roughness)
    )

    if not analysis_valid.any():
        raise ValueError("No valid pixels remain after analysis masks")

    slope_values = slope[analysis_valid]
    roughness_values = roughness[analysis_valid]
    tpi_values = tpi[analysis_valid]

    slope_p30, slope_p80 = np.percentile(
        slope_values, [30, 80]
    )

    rough_p30, rough_p80 = np.percentile(
        roughness_values, [30, 80]
    )

    tpi_median = np.median(tpi_values)
    tpi_std = np.std(tpi_values)
    abs_tpi_median = np.median(np.abs(tpi_values))

    classes = np.zeros(dem_shape, dtype=np.uint8)

    ridge = (
        analysis_valid &
        (tpi > tpi_median + tpi_std)
    )

    valley = (
        analysis_valid &
        (tpi < tpi_median - tpi_std)
    )

    rugged = (
        analysis_valid &
        ~ridge &
        ~valley &
        (
            (slope >= slope_p80) |
            (roughness >= rough_p80)
        )
    )

    flat = (
        analysis_valid &
        ~ridge &
        ~valley &
        ~rugged &
        (slope <= slope_p30) &
        (roughness <= rough_p30) &
        (np.abs(tpi) <= abs_tpi_median)
    )

    rolling = (
        analysis_valid &
        ~ridge &
        ~valley &
        ~rugged &
        ~flat
    )

    classes[flat] = 1
    classes[rolling] = 2
    classes[rugged] = 3
    classes[ridge] = 4
    classes[valley] = 5

    CLASSIFICATION_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        CLASSIFICATION_FOLDER /
        f"{stem}_terrain_classification.tif"
    )

    output_profile = dem_profile.copy()
    output_profile.update(
        driver="GTiff",
        count=1,
        dtype="uint8",
        nodata=NODATA_CLASS,
        compress="deflate"
    )

    with rasterio.open(output_path, "w", **output_profile) as dst:
        dst.write(classes, 1)
        dst.set_band_description(
            1, "terrain_classification"
        )
        dst.update_tags(
            tpi_scale_m=TPI_SCALE_M,
            min_valid_fraction=MIN_VALID_FRACTION,
            classification_method="per_tile_relative_percentiles",
            class_1="flat_smooth",
            class_2="rolling",
            class_3="rugged",
            class_4="relative_ridge",
            class_5="relative_valley",
            nodata_class=NODATA_CLASS
        )

    total = int(analysis_valid.sum())

    result = {
        "filename": filename,
        "raster_file": output_path.name,
        "valid_pixels": total,
        "tpi_window_x": window_x,
        "tpi_window_y": window_y,
        "mean_slope_degrees": float(np.mean(slope_values)),
        "mean_roughness_630m": float(np.mean(roughness_values)),
        "slope_p30": float(slope_p30),
        "slope_p80": float(slope_p80),
        "roughness_p30": float(rough_p30),
        "roughness_p80": float(rough_p80),
        "tpi_median": float(tpi_median),
        "tpi_std": float(tpi_std),
        "classification_method": "per_tile_relative_percentiles"
    }

    for class_id, class_name in CLASS_NAMES.items():
        count = int(np.count_nonzero(classes == class_id))

        result[f"{class_name}_pixels"] = count
        result[f"{class_name}_percent"] = (
            count / total * 100 if total else 0
        )

    return result


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Maximum number of new tiles to classify"
    )

    args = parser.parse_args()

    if args.limit < 1:
        raise ValueError("--limit must be at least 1")

    if not ARCHIVES:
        raise FileNotFoundError(
            f"No DEM ZIP archives found in {ARCHIVE_FOLDER}"
        )

    GLOBAL_ROOT.mkdir(parents=True, exist_ok=True)
    CLASSIFICATION_FOLDER.mkdir(parents=True, exist_ok=True)

    selected, conflicts = build_inventory()

    print("\nTERRATIME 4D - GLOBAL TERRAIN CLASSIFICATION")
    print("=" * 65)
    print("Archives:", len(ARCHIVES))
    print("Non-conflicting unique tiles:", len(selected))
    print("Conflicting filenames:", len(conflicts))

    if SUMMARY_FILE.exists():
        summaries = pd.read_csv(SUMMARY_FILE).to_dict("records")
    else:
        summaries = []

    if LOG_FILE.exists():
        logs = pd.read_csv(LOG_FILE).to_dict("records")
    else:
        logs = []

    completed = {
        row["filename"].lower()
        for row in summaries
        if row.get("filename")
        and row.get("raster_file")
        and (
            CLASSIFICATION_FOLDER / str(row["raster_file"])
        ).exists()
    }

    pending = [
        item for item in selected
        if item[0].lower() not in completed
    ]

    print("Already completed:", len(completed))
    print("Tiles remaining:", len(pending))

    batch = pending[:args.limit]

    for index, (filename, archive, info) in enumerate(
        batch, start=1
    ):
        print(f"\n[{index}/{len(batch)}] Classifying: {filename}")

        try:
            with tempfile.TemporaryDirectory(
                prefix="terratime_classification_"
            ) as tmp:
                temporary_dem = Path(tmp) / Path(filename).name

                with zipfile.ZipFile(archive) as z:
                    with z.open(info) as source:
                        with temporary_dem.open("wb") as destination:
                            shutil.copyfileobj(source, destination)

                result = classify_tile(temporary_dem, filename)

            summaries = [
                row for row in summaries
                if str(row.get("filename", "")).lower()
                != filename.lower()
            ]
            summaries.append(result)

            logs.append({
                "filename": filename,
                "archive": archive.name,
                "status": "SUCCESS",
                "error": ""
            })

            print("SUCCESS:", result["raster_file"])

        except Exception as error:
            print("FAILED:", error)

            logs.append({
                "filename": filename,
                "archive": archive.name,
                "status": "FAILED",
                "error": str(error)
            })

        pd.DataFrame(summaries).to_csv(
            SUMMARY_FILE, index=False
        )

        pd.DataFrame(logs).drop_duplicates(
            subset=["filename", "status", "archive"],
            keep="last"
        ).to_csv(LOG_FILE, index=False)

    print("\n" + "=" * 65)
    print("CLASSIFICATION BATCH FINISHED")
    print("Successful classification rows:", len(summaries))
    print("Classification rasters:", CLASSIFICATION_FOLDER)
    print("Summary:", SUMMARY_FILE)
    print("Processing log:", LOG_FILE)


if __name__ == "__main__":
    main()