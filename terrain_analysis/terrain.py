from pathlib import Path

import numpy as np
import rasterio


def analyze_terrain(file_path):
    """Calculate terrain metrics from an elevation raster."""

    file_path = Path(file_path)

    with rasterio.open(file_path) as dataset:
        elevation = dataset.read(1, masked=True).astype("float64")
        transform = dataset.transform
        bounds = dataset.bounds
        crs = dataset.crs

    values = elevation.filled(np.nan)
    valid = np.isfinite(values)

    if not valid.any():
        raise ValueError("No valid elevation data found.")

    # Approximate pixel spacing in metres.
    pixel_x = abs(transform.a)
    pixel_y = abs(transform.e)

    if crs and crs.is_geographic:
        # Convert degrees to approximate metres at the dataset latitude.
        latitude = (bounds.bottom + bounds.top) / 2
        pixel_x *= 111320 * np.cos(np.radians(latitude))
        pixel_y *= 111320

    # Calculate elevation gradients and slope.
    filled_values = np.where(
        valid,
        values,
        np.nanmean(values)
    )

    gradient_y, gradient_x = np.gradient(
        filled_values,
        pixel_y,
        pixel_x
    )

    slope = np.degrees(
        np.arctan(
            np.sqrt(
                gradient_x**2 + gradient_y**2
            )
        )
    )

    # Basic roughness:
    # local elevation range in a 3x3 neighbourhood.
    padded = np.pad(
        filled_values,
        1,
        mode="edge"
    )

    neighbourhoods = [
        padded[
            i:i + values.shape[0],
            j:j + values.shape[1]
        ]
        for i in range(3)
        for j in range(3)
    ]

    roughness = (
        np.maximum.reduce(neighbourhoods)
        - np.minimum.reduce(neighbourhoods)
    )

    # Basic terrain metrics.
    elevation_min = float(np.nanmin(values))
    elevation_max = float(np.nanmax(values))
    elevation_mean = float(np.nanmean(values))

    mean_slope = float(np.nanmean(slope[valid]))
    mean_roughness = float(np.nanmean(roughness[valid]))

    # Relief = difference between highest and lowest elevation.
    relief_m = elevation_max - elevation_min

    # Simple terrain morphology classification.
    # These are transparent heuristic thresholds for TERRATIME 4D.
    if mean_slope < 2 and mean_roughness < 5:
        terrain_class = "Flat"

    elif mean_slope < 5 and mean_roughness < 10:
        terrain_class = "Rolling"

    elif mean_slope < 15 and mean_roughness < 25:
        terrain_class = "Hilly"

    elif mean_slope < 30 and mean_roughness < 50:
        terrain_class = "Steep"

    else:
        terrain_class = "Rugged"

    return {
        "elevation_min_m": elevation_min,
        "elevation_max_m": elevation_max,
        "elevation_mean_m": elevation_mean,
        "slope_mean_degrees": mean_slope,
        "roughness_mean_m": mean_roughness,
        "relief_m": float(relief_m),
        "terrain_class": terrain_class,
        "valid_pixels": int(valid.sum()),
        "crs": str(crs),
    }


if __name__ == "__main__":
    print("TerraTime 4D | Terrain Analysis")
    print("Place an elevation raster in data/raw/earth")
    print("and update the input path before running.")