
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import distance_transform_edt, uniform_filter


# ---------------------------------------------------------
# TERRATIME 4D - MEMBER 2 ADVANCED TERRAIN ANALYSIS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"
OUTPUT_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "advanced_terrain"
)

SUMMARY_FILE = OUTPUT_FOLDER / "advanced_terrain_summary.csv"
FINGERPRINT_FILE = (
    OUTPUT_FOLDER / "terrain_personality_fingerprint.csv"
)

TARGET_SCALES_M = (270.0, 630.0, 1350.0)
MIN_VALID_FRACTION = 0.75
NODATA_OUTPUT = -9999.0

LOCATION_NAMES = {
    "N13_00_E077": "Bengaluru",
    "N19_00_W155": "Hawaii",
    "N64_00_W019": "Iceland",
    "S23_00_W069": "Atacama Desert",
    "S25_00_E135": "Australian Outback",
    "S77_00_E000": "Antarctica",
}


def get_location(file_name):
    """Identify the study location from the raster filename."""

    for code, name in LOCATION_NAMES.items():
        if code in file_name:
            return name

    return Path(file_name).stem


def nearest_odd_window(target_metres, pixel_metres):
    """Choose the nearest odd pixel-window size to a target distance."""

    approximate = max(3, int(round(target_metres / pixel_metres)))

    if approximate % 2 == 1:
        return approximate

    options = [approximate - 1, approximate + 1]

    return min(
        options,
        key=lambda size: abs(size * pixel_metres - target_metres)
    )


def fill_invalid_pixels(array, valid_mask):
    """Fill invalid cells from their nearest valid neighbour for derivatives."""

    if not valid_mask.any():
        raise ValueError("No valid pixels available for analysis.")

    if valid_mask.all():
        return array.copy()

    indices = distance_transform_edt(
        ~valid_mask,
        return_distances=False,
        return_indices=True
    )

    nearest_values = array[indices[0], indices[1]]
    filled = array.copy()
    filled[~valid_mask] = nearest_values[~valid_mask]

    return filled


def calculate_local_roughness(
    elevation,
    valid_mask,
    window_y,
    window_x
):
    """
    Calculate local elevation standard deviation.

    A minimum valid-neighbour fraction prevents unreliable edge
    calculations around masked or missing pixels.
    """

    window = (window_y, window_x)

    weights = uniform_filter(
        valid_mask.astype(np.float64),
        size=window,
        mode="nearest"
    )

    safe_elevation = np.where(valid_mask, elevation, 0.0)

    mean = (
        uniform_filter(safe_elevation, size=window, mode="nearest")
        / np.maximum(weights, 1e-12)
    )

    mean_square = (
        uniform_filter(
            safe_elevation ** 2,
            size=window,
            mode="nearest"
        )
        / np.maximum(weights, 1e-12)
    )

    variance = np.maximum(mean_square - mean ** 2, 0.0)

    roughness = np.sqrt(variance)

    output_valid = (
        valid_mask
        & (weights >= MIN_VALID_FRACTION)
    )

    roughness[~output_valid] = np.nan

    return roughness.astype(np.float32), output_valid


def calculate_slope(elevation, valid_mask, pixel_width_rows, pixel_height):
    """Calculate slope in degrees using ground distances in metres."""

    filled = fill_invalid_pixels(elevation, valid_mask)

    dz_drow = np.gradient(filled, axis=0)
    dz_dcolumn = np.gradient(filled, axis=1)

    dz_dy = dz_drow / pixel_height
    dz_dx = dz_dcolumn / pixel_width_rows[:, None]

    slope = np.degrees(
        np.arctan(np.sqrt(dz_dx ** 2 + dz_dy ** 2))
    )

    support = uniform_filter(
        valid_mask.astype(np.float64),
        size=3,
        mode="nearest"
    )

    slope_valid = (
        valid_mask
        & (support >= MIN_VALID_FRACTION)
    )

    slope[~slope_valid] = np.nan

    return slope.astype(np.float32), slope_valid


def gradient_magnitude(field, valid_mask, pixel_width_rows, pixel_height):
    """Calculate spatial change per metre in a terrain measurement."""

    filled = fill_invalid_pixels(field, valid_mask)

    gradient_y = np.gradient(filled, axis=0) / pixel_height
    gradient_x = (
        np.gradient(filled, axis=1)
        / pixel_width_rows[:, None]
    )

    magnitude = np.sqrt(gradient_x ** 2 + gradient_y ** 2)

    support = uniform_filter(
        valid_mask.astype(np.float64),
        size=3,
        mode="nearest"
    )

    output_valid = (
        valid_mask
        & (support >= MIN_VALID_FRACTION)
    )

    magnitude[~output_valid] = np.nan

    return magnitude.astype(np.float32), output_valid


def positive_robust_zscore(values, valid_mask):
    """Calculate non-negative robust z-scores using median and MAD."""

    selected = values[valid_mask]

    median = float(np.median(selected))
    mad = float(np.median(np.abs(selected - median)))

    scale = 1.4826 * mad

    if scale < 1e-12:
        scale = float(np.std(selected))

    result = np.full(values.shape, np.nan, dtype=np.float32)

    if scale < 1e-12:
        result[valid_mask] = 0.0
        return result

    zscore = (values - median) / scale
    result[valid_mask] = np.maximum(zscore[valid_mask], 0.0)

    return result


def calculate_statistics(array):
    """Return mean, median and 90th percentile for finite values."""

    values = array[np.isfinite(array)]

    if values.size == 0:
        return {
            "mean": np.nan,
            "median": np.nan,
            "p90": np.nan
        }

    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p90": float(np.percentile(values, 90))
    }


def save_analysis_raster(
    source_dataset,
    location,
    slope,
    roughness_layers,
    hidden_layer,
    transition_score,
    hotspot_layer
):
    """Save all spatial results as a multi-band GeoTIFF."""

    output_file = (
        OUTPUT_FOLDER
        / f"{location.lower().replace(' ', '_')}_advanced_terrain.tif"
    )

    layers = [
        ("slope_degrees", slope),
        ("roughness_270m", roughness_layers[270.0]),
        ("roughness_630m", roughness_layers[630.0]),
        ("roughness_1350m", roughness_layers[1350.0]),
        ("hidden_ruggedness_01", hidden_layer),
        ("transition_score", transition_score),
        ("transition_hotspot_01", hotspot_layer),
    ]

    profile = source_dataset.profile.copy()

    profile.update(
        driver="GTiff",
        count=len(layers),
        dtype="float32",
        nodata=NODATA_OUTPUT,
        compress="deflate"
    )

    with rasterio.open(output_file, "w", **profile) as destination:
        for band_number, (description, values) in enumerate(
            layers, start=1
        ):
            output_values = np.where(
                np.isfinite(values),
                values,
                NODATA_OUTPUT
            ).astype(np.float32)

            destination.write(output_values, band_number)
            destination.set_band_description(
                band_number, description
            )

        destination.update_tags(
            location=location,
            roughness_method="Local elevation standard deviation",
            hidden_ruggedness_rule=(
                "Slope <= tile P30 and 630m roughness >= tile P70"
            ),
            transition_rule=(
                "Combined positive robust z-scores of slope "
                "and 630m roughness gradients"
            ),
            hotspot_rule="Top 5th percentile within each tile",
            hawaii_mask="Provisional elevation greater than 1 metre"
        )

    return output_file


def analyze_raster(file_path):
    """Run all three advanced terrain analyses on one DEM tile."""

    location = get_location(file_path.name)

    with rasterio.open(file_path) as dataset:

        if dataset.crs is None or not dataset.crs.is_geographic:
            raise ValueError(
                f"{file_path.name} must use a geographic CRS."
            )

        elevation = (
            dataset.read(1, masked=True)
            .astype(np.float64)
            .filled(np.nan)
        )

        data_valid = np.isfinite(elevation)

        if not data_valid.any():
            raise ValueError(f"No valid pixels in {file_path.name}")

        height, width = elevation.shape
        transform = dataset.transform

        # Approximate ground resolution by latitude.
        row_latitudes = (
            transform.f
            + (np.arange(height) + 0.5) * transform.e
        )

        pixel_width_rows = (
            abs(transform.a)
            * 111320.0
            * np.cos(np.radians(row_latitudes))
        )

        pixel_width_mean = float(np.mean(pixel_width_rows))
        pixel_height = abs(transform.e) * 111320.0

        # Provisional project land filter for the Hawaii test tile.
        analysis_mask = data_valid.copy()
        mask_method = "All valid raster pixels"

        if "N19_00_W155" in file_path.name:
            analysis_mask &= elevation > 1.0
            mask_method = "Provisional elevation > 1 metre"

        if not analysis_mask.any():
            raise ValueError(f"No analysis pixels in {file_path.name}")

        # Calculate slope.
        slope, slope_valid = calculate_slope(
            elevation,
            analysis_mask,
            pixel_width_rows,
            pixel_height
        )

        # Calculate roughness at comparable ground-distance scales.
        roughness_layers = {}
        roughness_valid_masks = {}
        windows = {}

        for scale in TARGET_SCALES_M:
            window_x = nearest_odd_window(
                scale, pixel_width_mean
            )

            window_y = nearest_odd_window(
                scale, pixel_height
            )

            roughness, roughness_valid = calculate_local_roughness(
                elevation,
                analysis_mask,
                window_y,
                window_x
            )

            roughness_layers[scale] = roughness
            roughness_valid_masks[scale] = roughness_valid

            windows[scale] = (window_y, window_x)

        # -------------------------------------------------
        # FEATURE 1: TERRAIN PERSONALITY FINGERPRINT
        # -------------------------------------------------

        fingerprint = {
            "location": location,
            "raster_file": file_path.name,
            "pixel_width_mean_m": pixel_width_mean,
            "pixel_height_m": pixel_height,
            "analysis_pixels": int(analysis_mask.sum()),
        }

        summary = {
            "location": location,
            "raster_file": file_path.name,
            "raster_width": width,
            "raster_height": height,
            "raster_valid_pixels": int(data_valid.sum()),
            "analysis_pixels": int(analysis_mask.sum()),
            "mask_method": mask_method,
            "pixel_width_mean_m": pixel_width_mean,
            "pixel_height_m": pixel_height,
            "elevation_min_m": float(elevation[analysis_mask].min()),
            "elevation_max_m": float(elevation[analysis_mask].max()),
            "elevation_mean_m": float(elevation[analysis_mask].mean()),
        }

        for scale in TARGET_SCALES_M:
            roughness = roughness_layers[scale]
            stats = calculate_statistics(roughness)

            window_y, window_x = windows[scale]

            fingerprint[f"roughness_{int(scale)}m_mean"] = stats["mean"]
            fingerprint[f"roughness_{int(scale)}m_p90"] = stats["p90"]

            summary[f"roughness_{int(scale)}m_mean"] = stats["mean"]
            summary[f"roughness_{int(scale)}m_p90"] = stats["p90"]
            summary[f"roughness_{int(scale)}m_window"] = (
                f"{window_y}x{window_x}"
            )

        small_mean = fingerprint["roughness_270m_mean"]
        medium_mean = fingerprint["roughness_630m_mean"]
        large_mean = fingerprint["roughness_1350m_mean"]

        fingerprint["growth_630m_vs_270m"] = (
            medium_mean / small_mean
            if small_mean and np.isfinite(small_mean)
            else np.nan
        )

        fingerprint["growth_1350m_vs_270m"] = (
            large_mean / small_mean
            if small_mean and np.isfinite(small_mean)
            else np.nan
        )

        # -------------------------------------------------
        # FEATURE 2: HIDDEN RUGGEDNESS DETECTION
        # -------------------------------------------------

        medium_roughness = roughness_layers[630.0]

        hidden_valid = (
            slope_valid
            & np.isfinite(medium_roughness)
        )

        slope_values = slope[hidden_valid]
        roughness_values = medium_roughness[hidden_valid]

        slope_threshold = float(np.percentile(slope_values, 30))
        roughness_threshold = float(
            np.percentile(roughness_values, 70)
        )

        hidden_mask = (
            hidden_valid
            & (slope <= slope_threshold)
            & (medium_roughness >= roughness_threshold)
        )

        hidden_layer = np.where(
            hidden_valid,
            hidden_mask.astype(np.float32),
            np.nan
        )

        hidden_count = int(hidden_mask.sum())
        hidden_percentage = (
            100.0 * hidden_count / int(hidden_valid.sum())
        )

        summary["hidden_slope_p30_degrees"] = slope_threshold
        summary["hidden_roughness_p70_m"] = roughness_threshold
        summary["hidden_ruggedness_pixels"] = hidden_count
        summary["hidden_ruggedness_percent"] = hidden_percentage

        # -------------------------------------------------
        # FEATURE 3: TERRAIN TRANSITION HOTSPOTS
        # -------------------------------------------------

        slope_change, slope_change_valid = gradient_magnitude(
            slope,
            hidden_valid,
            pixel_width_rows,
            pixel_height
        )

        roughness_change, roughness_change_valid = gradient_magnitude(
            medium_roughness,
            hidden_valid,
            pixel_width_rows,
            pixel_height
        )

        transition_valid = (
            slope_change_valid
            & roughness_change_valid
        )

        slope_z = positive_robust_zscore(
            slope_change, transition_valid
        )

        roughness_z = positive_robust_zscore(
            roughness_change, transition_valid
        )

        transition_score = np.sqrt(
            slope_z ** 2 + roughness_z ** 2
        )

        transition_score[~transition_valid] = np.nan

        scores = transition_score[transition_valid]
        threshold = float(np.percentile(scores, 95))

        hotspot_mask = (
            transition_valid
            & (transition_score >= threshold)
            & (transition_score > 0)
        )

        hotspot_layer = np.where(
            transition_valid,
            hotspot_mask.astype(np.float32),
            np.nan
        )

        hotspot_count = int(hotspot_mask.sum())
        hotspot_percentage = (
            100.0 * hotspot_count / int(transition_valid.sum())
        )

        summary["transition_score_p95"] = threshold
        summary["transition_hotspot_pixels"] = hotspot_count
        summary["transition_hotspot_percent"] = hotspot_percentage

        transition_score_output = transition_score.copy()

        # Save the georeferenced output bands.
        output_file = save_analysis_raster(
            dataset,
            location,
            slope,
            roughness_layers,
            hidden_layer,
            transition_score_output,
            hotspot_layer
        )

    slope_stats = calculate_statistics(slope)

    summary["slope_mean_degrees"] = slope_stats["mean"]
    summary["slope_p90_degrees"] = slope_stats["p90"]

    print(f"\nCompleted: {location}")
    print("  Mean slope:", round(slope_stats["mean"], 2), "degrees")
    print("  630m roughness:", round(medium_mean, 2), "m")
    print("  Hidden ruggedness:", round(hidden_percentage, 2), "%")
    print("  Transition hotspots:", round(hotspot_percentage, 2), "%")
    print("  Output:", output_file.name)

    return summary, fingerprint


def main():
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    raster_files = sorted(INPUT_FOLDER.glob("*.tif"))

    if not raster_files:
        raise FileNotFoundError(
            f"No GeoTIFF files found in {INPUT_FOLDER}"
        )

    print("\nTERRATIME 4D - MEMBER 2 ADVANCED TERRAIN ANALYSIS")
    print("=" * 65)
    print("Raster files found:", len(raster_files))

    summary_rows = []
    fingerprint_rows = []

    for file_path in raster_files:
        summary, fingerprint = analyze_raster(file_path)

        summary_rows.append(summary)
        fingerprint_rows.append(fingerprint)

    pd.DataFrame(summary_rows).to_csv(
        SUMMARY_FILE, index=False
    )

    pd.DataFrame(fingerprint_rows).to_csv(
        FINGERPRINT_FILE, index=False
    )

    print("\n" + "=" * 65)
    print("ADVANCED TERRAIN ANALYSIS COMPLETE")
    print("Summary:", SUMMARY_FILE)
    print("Fingerprint:", FINGERPRINT_FILE)
    print("Map files:", OUTPUT_FOLDER)


if __name__ == "__main__":
    main()
