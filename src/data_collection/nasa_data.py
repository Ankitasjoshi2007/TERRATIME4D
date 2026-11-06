
"""
TERRATIME 4D
Member 1 - Earth Data Collection

Functions for discovering, loading, summarizing,
and exporting NASA SRTM elevation data.
"""

from pathlib import Path
import csv

import numpy as np
import rasterio


# Locate the project root automatically.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# NASA SRTM data directory.
SRTM_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "earth"

# Default inventory output path.
INVENTORY_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "nasa_srtm_tile_inventory.csv"
)


def find_srtm_tiles():
    """
    Find actual NASA SRTM HGT files, excluding directories.

    Returns:
        list[Path]: Paths to discovered HGT files.
    """
    if not SRTM_DATA_DIR.is_dir():
        raise FileNotFoundError(
            f"SRTM data directory not found: {SRTM_DATA_DIR}"
        )

    return sorted(
        path
        for path in SRTM_DATA_DIR.rglob("*.hgt")
        if path.is_file()
    )


def load_srtm_tile(file_path):
    """
    Open an SRTM HGT tile and return elevation data and metadata.

    Args:
        file_path: Path to an HGT file.

    Returns:
        tuple: Masked elevation array and raster metadata.
    """
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"SRTM HGT file not found or is not a file: {file_path}"
        )

    if file_path.suffix.lower() != ".hgt":
        raise ValueError(f"Expected an HGT file: {file_path}")

    with rasterio.open(file_path) as dataset:
        elevation = dataset.read(1, masked=True)
        metadata = dataset.meta.copy()

    return elevation, metadata


def get_elevation_summary(file_path):
    """
    Calculate basic elevation statistics for an SRTM tile.

    Returns:
        dict: Elevation statistics and spatial metadata.
    """
    elevation, metadata = load_srtm_tile(file_path)

    valid_values = elevation.compressed()

    if valid_values.size == 0:
        raise ValueError(
            f"The tile contains no valid elevation pixels: {file_path}"
        )

    return {
        "file": Path(file_path).name,
        "width": metadata["width"],
        "height": metadata["height"],
        "crs": str(metadata["crs"]),
        "resolution": metadata["transform"][0],
        "nodata": metadata["nodata"],
        "valid_pixels": int(valid_values.size),
        "minimum_elevation_m": float(np.min(valid_values)),
        "maximum_elevation_m": float(np.max(valid_values)),
        "mean_elevation_m": float(np.mean(valid_values)),
        "standard_deviation_m": float(np.std(valid_values)),
    }


def export_srtm_inventory(output_path=None):
    """
    Export discovered SRTM tile summaries to a CSV inventory.

    Args:
        output_path: Optional custom CSV output path.

    Returns:
        Path: Location of the generated CSV file.
    """
    if output_path is None:
        output_path = INVENTORY_OUTPUT

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tiles = find_srtm_tiles()

    if not tiles:
        raise FileNotFoundError(
            "No NASA SRTM HGT files were found."
        )

    summaries = [
        get_elevation_summary(tile)
        for tile in tiles
    ]

    fieldnames = list(summaries[0].keys())

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(summaries)

    print(f"SRTM inventory saved to: {output_path}")
    print(f"Number of tiles exported: {len(summaries)}")

    return output_path
