
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import uniform_filter1d


# ============================================================
# TERRATIME4D
# MEMBER 3 - GLOBAL PHYSICAL TERRAIN ANALYSIS - VERSION 3
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MOON_FILE = BASE_DIR / "data" / "raw" / "moon" / "ldem_16.tif"
MARS_FILE = BASE_DIR / "data" / "raw" / "mars" / "megt90n000eb.img"
EARTH_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "global_terrain"
    / "global_advanced_terrain_summary.csv"
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

    weighted_mean = np.average(data, weights=weights)

    return {
        "mean": float(np.mean(data)),
        "area_weighted_mean": float(weighted_mean),
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

    The neighbourhood is a local spherical-grid approximation,
    not an exact geodesic or circular window.
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
            local_mean,
            size=longitude_window,
            mode="wrap"
        )

        square_filtered = uniform_filter1d(
            local_mean_squared,
            size=longitude_window,
            mode="wrap"
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
            (latitudes >= lower)
            & (latitudes < upper)
        )

        if not np.any(row_mask):
            continue

        band_elevation = elevation[row_mask, :]
        band_slope = slope[row_mask, :]
        band_roughness = roughness[row_mask, :]

        records.append({
            "planet": planet_name,
            "latitude_band": f"{lower} to {upper}",
            "elevation_mean_km": float(
                np.nanmean(band_elevation)
            ),
            "elevation_min_km": float(
                np.nanmin(band_elevation)
            ),
            "elevation_max_km": float(
                np.nanmax(band_elevation)
            ),
            "slope_mean_degrees": float(
                np.nanmean(band_slope)
            ),
            "slope_p90_degrees": float(
                np.nanpercentile(band_slope, 90)
            ),
            "roughness_mean_km": float(
                np.nanmean(band_roughness)
            ),
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

    # Aggregate the original 16 pixels/degree grid to
    # 8 pixels/degree using 2 by 2 averaging.
    moon = moon.reshape(
        1440, 2, 2880, 2
    ).mean(axis=(1, 3))

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

    # Convert elevation from metres to kilometres.
    mars = mars.astype(np.float32) / 1000.0

    print("Mars data loaded.")

    return mars


def load_earth_reference():
    """Read existing Member 1 and Member 2 Earth statistics."""

    if not EARTH_FILE.exists():
        print("\nEarth reference CSV was not found.")
        return pd.DataFrame()

    print("\nLoading existing Earth reference statistics...")

    earth = pd.read_csv(EARTH_FILE)

    return earth.describe(include="all").transpose().reset_index(
        names="metric"
    )


def write_report(moon_summary, mars_summary, earth):
    """Write the Version 3 methodology and limitations report."""

    report_path = (
        OUTPUT_DIR / "member3_physical_analysis_report_v3.txt"
    )

    lines = [
        "TERRATIME4D",
        "MEMBER 3 - VERSION 3 PHYSICAL TERRAIN ANALYSIS",
        "=" * 65,
        "",
        "OBJECTIVE",
        "Analyse global Moon and Mars elevation grids using",
        "slope and approximately 11 km physical roughness.",
        "Use the existing processed Earth terrain summary as",
        "a separate reference.",
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
        "IMPORTANT DATA LIMITATIONS",
        "1. The Moon TIFF has no per-pixel direct-observation mask.",
        "2. Mars MEGDR includes interpolated values where direct",
        "   MOLA observations are unavailable.",
        "3. The roughness neighbourhood is a local rectangular",
        "   spherical-grid approximation, not an exact geodesic",
        "   or circular neighbourhood.",
        "4. Polar rows at absolute latitudes of 89 degrees or more",
        "   are excluded from slope and roughness calculations.",
        "5. Earth statistics represent 645 processed tiles only.",
        "   They are not a complete global Earth dataset.",
        "6. Earth roughness measurements use different spatial",
        "   scales and cannot be directly equated with the",
        "   approximately 11 km Moon and Mars measurements.",
        "7. Earth summary statistics are based on tile-level",
        "   values and are not pooled pixel-level global statistics.",
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
        "EARTH REFERENCE",
        f"Earth reference rows: {len(earth)}",
        "",
        "CONCLUSION",
        "The analysis provides a physical terrain comparison",
        "between the available Moon and Mars elevation grids.",
        "The existing Earth results provide a partial reference.",
        "Differences in source resolution, coverage, observation",
        "methods and roughness scales must be considered when",
        "interpreting comparisons.",
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

    earth_reference = load_earth_reference()

    earth_reference.to_csv(
        OUTPUT_DIR / "earth_existing_reference_statistics_v3.csv",
        index=False
    )

    write_report(
        moon_summary, mars_summary, earth_reference
    )

    print("\nVersion 3 analysis completed.")
    print(f"Output folder: {OUTPUT_DIR}")
    print("\nGenerated files:")
    for file in sorted(OUTPUT_DIR.iterdir()):
        print(file.name)


if __name__ == "__main__":
    main()
