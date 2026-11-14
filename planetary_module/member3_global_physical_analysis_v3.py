
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import uniform_filter1d


# ============================================================
# TERRATIME4D
# MEMBER 3 - GLOBAL PHYSICAL TERRAIN ANALYSIS - VERSION 3
# UPDATED EARTH REFERENCE: 648 UNIQUE SUMMARY RECORDS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MOON_FILE = BASE_DIR / "data" / "raw" / "moon" / "ldem_16.tif"
MARS_FILE = BASE_DIR / "data" / "raw" / "mars" / "megt90n000eb.img"

EARTH_FILE = (
    BASE_DIR / "data" / "processed" / "global_terrain"
    / "global_advanced_terrain_summary.csv"
)

EARTH_LOG_FILE = (
    BASE_DIR / "data" / "processed" / "global_terrain"
    / "global_processing_log.csv"
)

EARTH_CLASS_FILE = (
    BASE_DIR / "data" / "processed" / "global_terrain"
    / "global_terrain_classification_summary.csv"
)

OUTPUT_DIR = BASE_DIR / "results" / "member3_global_analysis_v3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MOON_RADIUS_KM = 1737.4
MARS_RADIUS_KM = 3396.0

TARGET_ROUGHNESS_KM = 11.0
POLAR_LIMIT_DEG = 89.0


def weighted_statistics(values, latitudes):
    """Calculate statistics using latitude-based area weights."""

    valid = np.isfinite(values)

    if not np.any(valid):
        return {}

    data = values[valid]
    lat_grid = np.broadcast_to(
        latitudes[:, None], values.shape
    )[valid]

    weights = np.cos(np.deg2rad(lat_grid))
    weights = np.maximum(weights, 0)

    return {
        "mean": float(np.mean(data)),
        "area_weighted_mean": float(np.average(data, weights=weights)),
        "median": float(np.median(data)),
        "p90": float(np.percentile(data, 90)),
        "minimum": float(np.min(data)),
        "maximum": float(np.max(data)),
        "valid_cells": int(len(data)),
    }


def calculate_slope(elevation, radius_km, pixels_per_degree, latitudes):
    """Calculate approximate terrain slope on a spherical grid."""

    dy = radius_km * np.deg2rad(1.0 / pixels_per_degree)
    gradient_y = np.gradient(elevation, dy, axis=0)

    longitude_spacing = (
        radius_km
        * np.cos(np.deg2rad(latitudes))
        * np.deg2rad(1.0 / pixels_per_degree)
    )

    longitude_spacing = np.maximum(
        np.abs(longitude_spacing), 1e-8
    )

    gradient_x = np.empty_like(elevation, dtype=np.float64)

    for row in range(elevation.shape[0]):
        gradient_x[row] = (
            np.gradient(elevation[row]) / longitude_spacing[row]
        )

    slope = np.rad2deg(
        np.arctan(np.sqrt(gradient_x**2 + gradient_y**2))
    )

    slope[np.abs(latitudes) >= POLAR_LIMIT_DEG, :] = np.nan

    return slope


def calculate_physical_roughness(
    elevation, radius_km, pixels_per_degree, latitudes
):
    """
    Estimate local elevation standard deviation using an
    approximately 11 km by 11 km neighbourhood.

    This is a local spherical-grid approximation, not an exact
    geodesic or circular neighbourhood.
    """

    rows, columns = elevation.shape

    roughness = np.full(
        (rows, columns), np.nan, dtype=np.float32
    )

    pixel_angle = np.deg2rad(1.0 / pixels_per_degree)
    north_south_spacing = radius_km * pixel_angle

    row_window = max(
        1, int(round(TARGET_ROUGHNESS_KM / north_south_spacing))
    )

    if row_window % 2 == 0:
        row_window += 1

    half_rows = row_window // 2

    for row in range(rows):

        latitude = latitudes[row]

        if abs(latitude) >= POLAR_LIMIT_DEG:
            continue

        east_west_spacing = (
            radius_km
            * np.cos(np.deg2rad(latitude))
            * pixel_angle
        )

        if east_west_spacing <= 0:
            continue

        longitude_window = max(
            1,
            int(round(TARGET_ROUGHNESS_KM / east_west_spacing))
        )

        if longitude_window % 2 == 0:
            longitude_window += 1

        longitude_window = min(longitude_window, columns)

        if longitude_window % 2 == 0:
            longitude_window -= 1

        selected_rows = [
            min(max(row + offset, 0), rows - 1)
            for offset in range(-half_rows, half_rows + 1)
        ]

        local_rows = elevation[selected_rows, :].astype(
            np.float64, copy=False
        )

        local_mean = np.mean(local_rows, axis=0)
        local_mean_squared = np.mean(local_rows**2, axis=0)

        mean_filtered = uniform_filter1d(
            local_mean, size=longitude_window, mode="wrap"
        )

        square_filtered = uniform_filter1d(
            local_mean_squared, size=longitude_window, mode="wrap"
        )

        variance = np.maximum(
            square_filtered - mean_filtered**2, 0
        )

        roughness[row, :] = np.sqrt(variance).astype(np.float32)

    return roughness


def calculate_latitude_bands(
    planet_name, elevation, slope, roughness, latitudes
):
    """Create physical terrain statistics for 10-degree bands."""

    records = []

    for lower in range(-90, 90, 10):
        upper = lower + 10

        row_mask = (
            (latitudes >= lower) & (latitudes < upper)
        )

        if not np.any(row_mask):
            continue

        band_elevation = elevation[row_mask, :]
        band_slope = slope[row_mask, :]
        band_roughness = roughness[row_mask, :]

        records.append({
            "planet": planet_name,
            "latitude_band": f"{lower} to {upper}",
            "elevation_mean_km": float(np.nanmean(band_elevation)),
            "elevation_min_km": float(np.nanmin(band_elevation)),
            "elevation_max_km": float(np.nanmax(band_elevation)),
            "slope_mean_degrees": float(np.nanmean(band_slope)),
            "slope_p90_degrees": float(
                np.nanpercentile(band_slope, 90)
            ),
            "roughness_mean_km": float(np.nanmean(band_roughness)),
            "roughness_p90_km": float(
                np.nanpercentile(band_roughness, 90)
            ),
        })

    return records


def analyse_planet(
    planet_name, elevation, radius_km, pixels_per_degree
):
    """Run physical terrain analysis for one planetary body."""

    print(f"\nStarting {planet_name} analysis...")

    rows = elevation.shape[0]

    latitudes = np.linspace(
        90.0 - 0.5 / pixels_per_degree,
        -90.0 + 0.5 / pixels_per_degree,
        rows
    )

    print("Calculating slope...")
    slope = calculate_slope(
        elevation, radius_km, pixels_per_degree, latitudes
    )

    print("Calculating approximately 11 km physical roughness...")
    roughness = calculate_physical_roughness(
        elevation, radius_km, pixels_per_degree, latitudes
    )

    elevation_stats = weighted_statistics(elevation, latitudes)
    slope_stats = weighted_statistics(slope, latitudes)
    roughness_stats = weighted_statistics(roughness, latitudes)

    equatorial_pixel_size = (
        radius_km * np.deg2rad(1.0 / pixels_per_degree)
    )

    summary = {
        "planet": planet_name,
        "rows": int(elevation.shape[0]),
        "columns": int(elevation.shape[1]),
        "total_cells": int(elevation.size),
        "elevation_min_km": float(np.nanmin(elevation)),
        "elevation_max_km": float(np.nanmax(elevation)),
        "elevation_grid_mean_km": float(np.nanmean(elevation)),
        "elevation_area_weighted_mean_km":
            elevation_stats["area_weighted_mean"],
        "slope_mean_degrees": slope_stats["mean"],
        "slope_area_weighted_mean_degrees":
            slope_stats["area_weighted_mean"],
        "slope_median_degrees": slope_stats["median"],
        "slope_p90_degrees": slope_stats["p90"],
        "slope_valid_cells": slope_stats["valid_cells"],
        "roughness_mean_km": roughness_stats["mean"],
        "roughness_area_weighted_mean_km":
            roughness_stats["area_weighted_mean"],
        "roughness_median_km": roughness_stats["median"],
        "roughness_p90_km": roughness_stats["p90"],
        "roughness_valid_cells": roughness_stats["valid_cells"],
        "equatorial_pixel_size_km": equatorial_pixel_size,
        "roughness_target_km": TARGET_ROUGHNESS_KM,
    }

    bands = calculate_latitude_bands(
        planet_name, elevation, slope, roughness, latitudes
    )

    print(f"{planet_name} analysis completed.")

    return summary, bands


def load_moon():
    """Load NASA global lunar elevation TIFF."""

    print("\nLoading Moon elevation data...")

    with rasterio.open(MOON_FILE) as dataset:
        moon = dataset.read(1).astype(np.float32)

    if moon.shape != (2880, 5760):
        raise ValueError(
            f"Unexpected Moon raster shape: {moon.shape}"
        )

    moon = moon.reshape(1440, 2, 2880, 2).mean(axis=(1, 3))

    print("Moon data loaded and aggregated.")

    return moon


def load_mars():
    """Load NASA MOLA MEGDR signed 16-bit elevation data."""

    print("\nLoading Mars elevation data...")

    mars = np.fromfile(MARS_FILE, dtype=">i2")

    expected_pixels = 2880 * 5760

    if mars.size != expected_pixels:
        raise ValueError(
            f"Unexpected Mars pixel count: {mars.size}"
        )

    mars = mars.reshape(2880, 5760)
    mars = mars.astype(np.float32) / 1000.0

    print("Mars data loaded.")

    return mars


def load_earth_reference():
    """
    Load all Earth tile-level records and calculate descriptive
    statistics. Keep the original 648 rows separate from the
    descriptive-statistics output.
    """

    if not EARTH_FILE.exists():
        raise FileNotFoundError(
            f"Earth reference CSV not found: {EARTH_FILE}"
        )

    print("\nLoading updated Earth reference statistics...")

    earth = pd.read_csv(EARTH_FILE)

    if "location" not in earth.columns:
        raise ValueError("Earth summary is missing the location column.")

    if earth["location"].duplicated().any():
        raise ValueError("Duplicate Earth locations were detected.")

    expected_columns = [
        "elevation_mean_m",
        "slope_mean_degrees",
        "roughness_270m_mean",
        "roughness_630m_mean",
        "roughness_1350m_mean",
    ]

    for column in expected_columns:
        if column not in earth.columns:
            raise ValueError(f"Missing Earth metric: {column}")

    earth_count = len(earth)
    unique_count = earth["location"].nunique()

    if earth_count != 648 or unique_count != 648:
        raise ValueError(
            f"Expected 648 unique Earth records; found "
            f"{earth_count} rows and {unique_count} unique locations."
        )

    # Export the complete original Earth reference records.
    earth.to_csv(
        OUTPUT_DIR / "earth_reference_tile_records_v3.csv",
        index=False
    )

    # Calculate descriptive statistics across the 648 tile-level
    # values. These are not pooled pixel-level global statistics.
    selected = earth[expected_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    earth_statistics = selected.describe().transpose().reset_index(
        names="metric"
    )

    earth_statistics.to_csv(
        OUTPUT_DIR / "earth_existing_reference_statistics_v3.csv",
        index=False
    )

    # Count processing and classification records independently.
    log_count = (
        len(pd.read_csv(EARTH_LOG_FILE))
        if EARTH_LOG_FILE.exists() else None
    )

    classification_count = (
        len(pd.read_csv(EARTH_CLASS_FILE))
        if EARTH_CLASS_FILE.exists() else None
    )

    # Identify records present in the advanced summary but absent
    # from successful processing-log filenames.
    extra_records = []

    if EARTH_LOG_FILE.exists():
        log = pd.read_csv(EARTH_LOG_FILE)

        if {"filename", "status"}.issubset(log.columns):
            successful_files = set(
                log.loc[
                    log["status"].astype(str).str.lower() == "success",
                    "filename"
                ].astype(str)
            )

            extra_records = earth.loc[
                ~earth["raster_file"].astype(str).isin(successful_files),
                "raster_file"
            ].astype(str).tolist()

    pd.DataFrame({
        "summary_only_raster_file": extra_records
    }).to_csv(
        OUTPUT_DIR / "earth_summary_only_records_v3.csv",
        index=False
    )

    audit = pd.DataFrame([{
        "advanced_summary_records": earth_count,
        "unique_locations": unique_count,
        "processing_log_records": log_count,
        "classification_summary_records": classification_count,
        "summary_only_records": len(extra_records),
        "earth_tile_mean_elevation_m":
            selected["elevation_mean_m"].mean(),
        "earth_tile_mean_slope_degrees":
            selected["slope_mean_degrees"].mean(),
        "earth_tile_mean_roughness_270m_m":
            selected["roughness_270m_mean"].mean(),
        "earth_tile_mean_roughness_630m_m":
            selected["roughness_630m_mean"].mean(),
        "earth_tile_mean_roughness_1350m_m":
            selected["roughness_1350m_mean"].mean(),
    }])

    audit.to_csv(
        OUTPUT_DIR / "earth_reference_audit_v3.csv",
        index=False
    )

    print(f"Earth advanced summary records: {earth_count}")
    print(f"Unique Earth locations: {unique_count}")
    print(f"Processing log records: {log_count}")
    print(f"Classification summary records: {classification_count}")
    print(f"Summary-only additional records: {len(extra_records)}")

    return earth_statistics, audit, extra_records


def write_report(moon_summary, mars_summary, earth_statistics, audit,
                 extra_records):
    """Write the Version 3 methodology and limitations report."""

    report_path = (
        OUTPUT_DIR / "member3_physical_analysis_report_v3.txt"
    )

    earth_row = audit.iloc[0]

    lines = [
        "TERRATIME4D",
        "MEMBER 3 - VERSION 3 PHYSICAL TERRAIN ANALYSIS",
        "=" * 65,
        "",
        "OBJECTIVE",
        "Analyse global Moon and Mars elevation grids using",
        "slope and approximately 11 km physical roughness.",
        "Use the latest processed Earth terrain summary as a",
        "separate reference dataset.",
        "",
        "METHOD",
        "Moon source: NASA Lunar Digital Elevation Model.",
        "Moon grid: aggregated from 16 to 8 pixels per degree.",
        "Mars source: NASA MOLA MEGDR elevation model.",
        "Mars grid: 16 pixels per degree.",
        "Slope: spherical-grid finite-difference approximation.",
        "Roughness: local elevation standard deviation.",
        "Roughness target: approximately 11 km by 11 km.",
        "Latitude bands: 10-degree intervals.",
        "Area weighting: cosine of latitude.",
        "",
        "EARTH REFERENCE DATA AUDIT",
        f"Advanced terrain summary records: {int(earth_row['advanced_summary_records'])}",
        f"Unique Earth locations: {int(earth_row['unique_locations'])}",
        f"Processing log records: {int(earth_row['processing_log_records'])}",
        f"Classification summary records: {int(earth_row['classification_summary_records'])}",
        f"Additional summary-only records: {int(earth_row['summary_only_records'])}",
        "",
        "Earth reference values are arithmetic averages of tile-level",
        "summary values. They are not pooled pixel-level global averages.",
        "The three additional summary records have valid terrain metrics",
        "but are absent from the processing log and classification summary.",
        "",
        "EARTH TILE-LEVEL REFERENCE AVERAGES",
        f"Mean tile elevation: {earth_row['earth_tile_mean_elevation_m']:.4f} m",
        f"Mean tile slope: {earth_row['earth_tile_mean_slope_degrees']:.6f} degrees",
        f"Mean roughness at 270 m: {earth_row['earth_tile_mean_roughness_270m_m']:.6f} m",
        f"Mean roughness at 630 m: {earth_row['earth_tile_mean_roughness_630m_m']:.6f} m",
        f"Mean roughness at 1350 m: {earth_row['earth_tile_mean_roughness_1350m_m']:.6f} m",
        "",
        "IMPORTANT DATA LIMITATIONS",
        "1. The Moon TIFF has no per-pixel direct-observation mask.",
        "2. Mars MEGDR includes interpolated values where direct",
        "   MOLA observations are unavailable.",
        "3. The roughness neighbourhood is a local rectangular",
        "   spherical-grid approximation, not an exact geodesic",
        "   or circular neighbourhood.",
        "4. Polar rows at absolute latitudes of 89 degrees or more",
        "   are excluded from slope and roughness calculations.",
        "5. Earth reference data contain 648 unique tile summaries;",
        "   this is not a complete global Earth dataset.",
        "6. Earth roughness measurements use 270 m, 630 m and 1350 m",
        "   scales, whereas Moon and Mars use approximately 11 km.",
        "   These roughness measurements are not directly equivalent.",
        "7. Earth summary statistics are based on tile-level values,",
        "   not pooled pixel-level global statistics.",
        "",
        "MOON RESULTS",
    ]

    for key, value in moon_summary.items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "MARS RESULTS"])

    for key, value in mars_summary.items():
        lines.append(f"{key}: {value}")

    lines.extend([
        "",
        "SUMMARY-ONLY EARTH RECORDS",
        *[f"- {name}" for name in extra_records],
        "",
        "CONCLUSION",
        "The analysis provides a physical terrain comparison",
        "between the available Moon and Mars elevation grids.",
        "The updated 648-record Earth reference provides a partial",
        "tile-level comparison. Differences in source resolution,",
        "coverage, observation methods and roughness scales must",
        "be considered when interpreting planetary analogies.",
        "",
    ])

    report_path.write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main():
    print("=" * 65)
    print("TERRATIME4D - MEMBER 3 - VERSION 3")
    print("=" * 65)

    moon = load_moon()
    mars = load_mars()

    moon_summary, moon_bands = analyse_planet(
        "Moon", moon, MOON_RADIUS_KM, 8
    )

    mars_summary, mars_bands = analyse_planet(
        "Mars", mars, MARS_RADIUS_KM, 16
    )

    summary = pd.DataFrame([
        moon_summary,
        mars_summary
    ])

    summary.to_csv(
        OUTPUT_DIR / "moon_mars_physical_summary_v3.csv",
        index=False
    )

    all_bands = pd.DataFrame(
        moon_bands + mars_bands
    )

    all_bands.to_csv(
        OUTPUT_DIR / "moon_mars_latitude_band_analysis_v3.csv",
        index=False
    )

    earth_statistics, earth_audit, extra_records = (
        load_earth_reference()
    )

    write_report(
        moon_summary,
        mars_summary,
        earth_statistics,
        earth_audit,
        extra_records
    )

    print("\nVersion 3 analysis completed.")
    print(f"Output folder: {OUTPUT_DIR}")
    print("\nGenerated files:")

    for file in sorted(OUTPUT_DIR.iterdir()):
        print(file.name)


if __name__ == "__main__":
    main()
