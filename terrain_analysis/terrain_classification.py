
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import uniform_filter


ROOT = Path(__file__).resolve().parents[1]

DEM_FOLDER = ROOT / "data" / "copernicus_glo90"
ADVANCED_FOLDER = ROOT / "data" / "processed" / "advanced_terrain"

OUTPUT_CSV = ADVANCED_FOLDER / "terrain_classification.csv"
MAP_FOLDER = ROOT / "terrain_analysis" / "terrain_maps" / "classification"

TPI_SCALE_M = 1000.0
MIN_VALID_FRACTION = 0.75
NODATA_CLASS = 0

LOCATIONS = {
    "N13_00_E077": ("bengaluru", "Bengaluru"),
    "N19_00_W155": ("hawaii", "Hawaii"),
    "N64_00_W019": ("iceland", "Iceland"),
    "S23_00_W069": ("atacama_desert", "Atacama Desert"),
    "S25_00_E135": ("australian_outback", "Australian Outback"),
    "S77_00_E000": ("antarctica", "Antarctica"),
}

CLASS_NAMES = {
    1: "Flat / smooth",
    2: "Rolling",
    3: "Rugged",
    4: "Relative ridge",
    5: "Relative valley",
}


def odd_window(distance_m, pixel_m):
    """Choose an odd-sized window near the requested ground distance."""

    size = max(3, int(round(distance_m / pixel_m)))

    if size % 2 == 0:
        size += 1

    return size


def calculate_tpi(elevation, valid_mask, window):
    """
    Calculate Topographic Position Index.

    TPI = central elevation - mean neighbourhood elevation.
    Positive values indicate relatively elevated terrain.
    Negative values indicate relatively depressed terrain.
    """

    weights = uniform_filter(
        valid_mask.astype(np.float64),
        size=window,
        mode="constant",
        cval=0.0
    )

    safe_elevation = np.where(valid_mask, elevation, 0.0)

    local_sum = uniform_filter(
        safe_elevation,
        size=window,
        mode="constant",
        cval=0.0
    )

    local_mean = local_sum / np.maximum(weights, 1e-12)

    tpi = elevation - local_mean

    tpi_valid = valid_mask & (weights >= MIN_VALID_FRACTION)
    tpi[~tpi_valid] = np.nan

    return tpi, tpi_valid


def find_location(filename):
    """Identify the location using its DEM tile name."""

    for code, details in LOCATIONS.items():
        if code in filename:
            return details

    raise ValueError(f"Unrecognised DEM filename: {filename}")


def analyse_tile(dem_path):
    """Classify terrain using slope, roughness and TPI."""

    short_name, location = find_location(dem_path.name)

    advanced_path = (
        ADVANCED_FOLDER / f"{short_name}_advanced_terrain.tif"
    )

    if not advanced_path.exists():
        raise FileNotFoundError(
            f"Advanced terrain raster not found: {advanced_path}"
        )

    with rasterio.open(dem_path) as dem:

        elevation = (
            dem.read(1, masked=True)
            .astype(np.float64)
            .filled(np.nan)
        )

        valid = np.isfinite(elevation)

        # Keep the same provisional Hawaii filter as the
        # existing Member 2 analysis.
        mask_note = "All finite DEM pixels"

        if "N19_00_W155" in dem_path.name:
            valid &= elevation > 1.0
            mask_note = "Provisional elevation > 1 metre"

        latitude = (dem.bounds.bottom + dem.bounds.top) / 2

        pixel_width = (
            abs(dem.transform.a)
            * 111320.0
            * np.cos(np.radians(latitude))
        )

        pixel_height = abs(dem.transform.e) * 111320.0

        window_x = odd_window(TPI_SCALE_M, pixel_width)
        window_y = odd_window(TPI_SCALE_M, pixel_height)

        tpi, tpi_valid = calculate_tpi(
            elevation,
            valid,
            window=(window_y, window_x)
        )

        # Read the already calculated slope and roughness layers.
        with rasterio.open(advanced_path) as advanced:

            descriptions = {
                name: index + 1
                for index, name in enumerate(advanced.descriptions)
            }

            required = {"slope_degrees", "roughness_630m"}

            if not required.issubset(descriptions):
                raise ValueError(
                    f"Required bands missing in {advanced_path.name}"
                )

            slope = (
                advanced.read(
                    descriptions["slope_degrees"],
                    masked=True
                )
                .astype(np.float64)
                .filled(np.nan)
            )

            roughness = (
                advanced.read(
                    descriptions["roughness_630m"],
                    masked=True
                )
                .astype(np.float64)
                .filled(np.nan)
            )

        analysis_valid = (
            valid
            & tpi_valid
            & np.isfinite(slope)
            & np.isfinite(roughness)
        )

        if not analysis_valid.any():
            raise ValueError(f"No valid classification pixels: {location}")

        slope_values = slope[analysis_valid]
        rough_values = roughness[analysis_valid]
        tpi_values = tpi[analysis_valid]

        # Relative thresholds are calculated separately per tile.
        slope_p30, slope_p80 = np.percentile(
            slope_values, [30, 80]
        )

        rough_p30, rough_p80 = np.percentile(
            rough_values, [30, 80]
        )

        tpi_median = float(np.median(tpi_values))
        tpi_std = float(np.std(tpi_values))

        # Initialise zero as NoData.
        classes = np.zeros(elevation.shape, dtype=np.uint8)

        # Relative topographic position.
        ridge = (
            analysis_valid
            & (tpi > tpi_median + tpi_std)
        )

        valley = (
            analysis_valid
            & (tpi < tpi_median - tpi_std)
        )

        classes[ridge] = 4
        classes[valley] = 5

        remaining = analysis_valid & (classes == 0)

        # Steeper or locally rougher terrain.
        rugged = remaining & (
            (slope >= slope_p80)
            | (roughness >= rough_p80)
        )

        classes[rugged] = 3

        remaining = analysis_valid & (classes == 0)

        # Smooth local terrain with low relative position variation.
        abs_tpi = np.abs(tpi_values)
        tpi_abs_p50 = float(np.percentile(abs_tpi, 50))

        flat = (
            remaining
            & (slope <= slope_p30)
            & (roughness <= rough_p30)
            & (np.abs(tpi) <= tpi_abs_p50)
        )

        classes[flat] = 1

        # All remaining valid terrain is placed in the rolling class.
        rolling = analysis_valid & (classes == 0)
        classes[rolling] = 2

        # Calculate per-class statistics.
        total = int(analysis_valid.sum())

        result = {
            "location": location,
            "raster_file": dem_path.name,
            "valid_classification_pixels": total,
            "tpi_window_pixels": f"{window_y}x{window_x}",
            "tpi_target_scale_m": TPI_SCALE_M,
            "land_mask_method": mask_note,
            "slope_p30_degrees": float(slope_p30),
            "slope_p80_degrees": float(slope_p80),
            "roughness_p30_m": float(rough_p30),
            "roughness_p80_m": float(rough_p80),
            "tpi_median_m": tpi_median,
            "tpi_standard_deviation_m": tpi_std,
        }

        for code, class_name in CLASS_NAMES.items():

            count = int(np.count_nonzero(classes == code))

            percentage = 100.0 * count / total

            key = (
                class_name.lower()
                .replace(" / ", "_")
                .replace(" ", "_")
            )

            result[f"{key}_pixels"] = count
            result[f"{key}_percent"] = percentage

        # Save a georeferenced classification map.
        MAP_FOLDER.mkdir(parents=True, exist_ok=True)

        map_path = MAP_FOLDER / f"{short_name}_terrain_classification.tif"

        profile = dem.profile.copy()

        profile.update(
            driver="GTiff",
            count=1,
            dtype="uint8",
            nodata=NODATA_CLASS,
            compress="deflate"
        )

        with rasterio.open(map_path, "w", **profile) as output:

            output.write(classes, 1)

            output.set_band_description(
                1, "Morphometric terrain classification"
            )

            output.update_tags(
                class_1="Flat / smooth",
                class_2="Rolling",
                class_3="Rugged",
                class_4="Relative ridge",
                class_5="Relative valley",
                tpi_scale_metres=TPI_SCALE_M,
                threshold_method="Relative per-tile percentiles",
                geological_identity="Not determined by this classification"
            )

    print(f"\nProcessed: {location}")
    print(f"  Valid pixels: {total:,}")
    print(f"  TPI window: {window_y} x {window_x}")
    print(f"  Classification map: {map_path.name}")

    return result


def main():

    ADVANCED_FOLDER.mkdir(parents=True, exist_ok=True)

    dem_files = sorted(DEM_FOLDER.glob("*.tif"))

    if not dem_files:
        raise FileNotFoundError(
            f"No DEM files found in {DEM_FOLDER}"
        )

    results = []

    print("\nTERRATIME 4D - MEMBER 2 TERRAIN CLASSIFICATION")
    print("=" * 60)

    for dem_path in dem_files:

        result = analyse_tile(dem_path)

        results.append(result)

    pd.DataFrame(results).to_csv(
        OUTPUT_CSV,
        index=False
    )

    print("\n" + "=" * 60)
    print("TERRAIN CLASSIFICATION COMPLETE")
    print("Summary:", OUTPUT_CSV)
    print("Maps:", MAP_FOLDER)


if __name__ == "__main__":
    main()
