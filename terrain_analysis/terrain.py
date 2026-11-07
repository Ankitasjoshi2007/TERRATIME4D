
from pathlib import Path

import numpy as np
import rasterio


def analyze_terrain(file_path):
    """Calculate basic terrain metrics from an elevation raster."""

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
        # Convert degrees to approximate metres at the dataset's latitude.
        latitude = (bounds.bottom + bounds.top) / 2
        pixel_x *= 111320 * np.cos(np.radians(latitude))
        pixel_y *= 111320

    # Calculate elevation gradients and slope.
    safe_values = np.where(valid, values, np.nan)
    filled_values = np.where(valid, values, np.nanmean(values))

    gradient_y, gradient_x = np.gradient(
        filled_values, pixel_y, pixel_x
    )

    slope = np.degrees(
        np.arctan(np.sqrt(gradient_x**2 + gradient_y**2))
    )

    # Basic roughness: local elevation range in a 3x3 neighbourhood.
    padded = np.pad(filled_values, 1, mode="edge")
    neighbourhoods = [
        padded[i:i + values.shape[0], j:j + values.shape[1]]
        for i in range(3)
        for j in range(3)
    ]
    roughness = (
        np.maximum.reduce(neighbourhoods)
        - np.minimum.reduce(neighbourhoods)
    )

    return {
        "elevation_min_m": float(np.nanmin(safe_values)),
        "elevation_max_m": float(np.nanmax(safe_values)),
        "elevation_mean_m": float(np.nanmean(safe_values)),
        "slope_mean_degrees": float(np.nanmean(slope[valid])),
        "roughness_mean_m": float(np.nanmean(roughness[valid])),
        "valid_pixels": int(valid.sum()),
        "crs": str(crs),
    }


if __name__ == "__main__":
    print("TerraTime 4D | Terrain Analysis")
    print("Place an extracted NASA .hgt or supported elevation raster")
    print("in data/raw/earth, then update the input path before running.")
