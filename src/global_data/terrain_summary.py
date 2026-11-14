from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_terrain_features.csv"
)

ROUGHNESS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_roughness_summary.csv"
)


def classify_terrain(mean_slope, mean_roughness):
    """Classify terrain morphology using transparent heuristic thresholds."""

    if mean_slope < 2 and mean_roughness < 5:
        return "Flat"

    elif mean_slope < 5 and mean_roughness < 10:
        return "Rolling"

    elif mean_slope < 15 and mean_roughness < 25:
        return "Hilly"

    elif mean_slope < 30 and mean_roughness < 50:
        return "Steep"

    else:
        return "Rugged"


def analyze_tile(file_path):
    """Calculate elevation, slope, and relief statistics for one DEM tile."""

    with rasterio.open(file_path) as dataset:

        elevation = dataset.read(1, masked=True).astype("float64")
        elevation = elevation.filled(np.nan)

        # Exclude invalid and non-finite elevation values.
        valid_mask = np.isfinite(elevation)

        # Provisional ocean exclusion for the Hawaii tile.
        # This is not a universal land/water classification method.
        # Replace with a proper coastline or land/water mask when available.
        if "N19_00_W155" in file_path.name:
            valid_mask &= elevation > 1.0

        if not np.any(valid_mask):
            return None

        # Calculate approximate pixel dimensions in metres.
        latitude = (
            dataset.bounds.bottom + dataset.bounds.top
        ) / 2

        pixel_width = (
            abs(dataset.transform.a)
            * 111320
            * np.cos(np.radians(latitude))
        )

        pixel_height = abs(dataset.transform.e) * 111320

        if (
            not np.isfinite(pixel_width)
            or not np.isfinite(pixel_height)
            or pixel_width <= 0
            or pixel_height <= 0
        ):
            raise ValueError(
                f"Invalid pixel dimensions in {file_path.name}"
            )

        # Replace invalid cells with NaN before calculating slope.
        elevation_for_slope = np.where(
            valid_mask, elevation, np.nan
        )

        # Pad the DEM so edge pixels do not wrap around.
        padded = np.pad(
            elevation_for_slope,
            1,
            mode="constant",
            constant_values=np.nan
        )

        center = padded[1:-1, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]
        top = padded[:-2, 1:-1]
        bottom = padded[2:, 1:-1]

        # Use central differences only where all five required
        # elevation values are valid.
        slope_mask = (
            np.isfinite(center)
            & np.isfinite(left)
            & np.isfinite(right)
            & np.isfinite(top)
            & np.isfinite(bottom)
        )

        dx = (right - left) / (2 * pixel_width)
        dy = (bottom - top) / (2 * pixel_height)

        slope = np.degrees(
            np.arctan(np.sqrt(dx**2 + dy**2))
        )

        valid_slope = slope[slope_mask]
        land_elevation = elevation[valid_mask]

        if land_elevation.size == 0 or valid_slope.size == 0:
            return None

        minimum_elevation = float(land_elevation.min())
        maximum_elevation = float(land_elevation.max())

        return {
            "location_tile": file_path.stem,
            "valid_elevation_pixels": int(land_elevation.size),
            "valid_slope_pixels": int(valid_slope.size),
            "minimum_elevation_m": round(
                minimum_elevation, 2
            ),
            "maximum_elevation_m": round(
                maximum_elevation, 2
            ),
            "average_elevation_m": round(
                float(land_elevation.mean()), 2
            ),
            "average_slope_degrees": round(
                float(valid_slope.mean()), 2
            ),
            "maximum_slope_degrees": round(
                float(valid_slope.max()), 2
            ),
            "relief_m": round(
                maximum_elevation - minimum_elevation,
                2
            ),
            "pixel_width_m_approx": round(
                float(pixel_width), 2
            ),
            "pixel_height_m_approx": round(
                float(pixel_height), 2
            )
        }


def main():
    files = sorted(DATA_FOLDER.glob("*.tif"))
    results = []

    print("\nTERRATIME 4D - GLOBAL TERRAIN FEATURES")
    print("-------------------------------------")

    if not files:
        print("No DEM files found:", DATA_FOLDER)
        return

    # Load existing global roughness results.
    roughness_data = {}

    if ROUGHNESS_FILE.exists():
        roughness_df = pd.read_csv(ROUGHNESS_FILE)

        for _, row in roughness_df.iterrows():
            roughness_data[row["tile"]] = float(
                row["average_roughness_m"]
            )

        print(
            "Loaded roughness data for",
            len(roughness_data),
            "tile(s)."
        )

    for file_path in files:
        try:
            result = analyze_tile(file_path)

            if result is None:
                print("Skipped:", file_path.name)
                continue

            tile_name = result["location_tile"]

            # Add existing roughness value.
            mean_roughness = roughness_data.get(
                tile_name,
                np.nan
            )

            result["average_roughness_m"] = (
                round(mean_roughness, 2)
                if np.isfinite(mean_roughness)
                else np.nan
            )

            # Classify terrain only when roughness is available.
            if np.isfinite(mean_roughness):
                result["terrain_class"] = classify_terrain(
                    result["average_slope_degrees"],
                    mean_roughness
                )
            else:
                result["terrain_class"] = "Unknown"

            results.append(result)

            print("\nProcessed:", file_path.name)
            print(
                "Average elevation:",
                result["average_elevation_m"],
                "m"
            )
            print(
                "Average slope:",
                result["average_slope_degrees"],
                "degrees"
            )
            print(
                "Relief:",
                result["relief_m"],
                "m"
            )
            print(
                "Terrain class:",
                result["terrain_class"]
            )

        except Exception as error:
            print(
                "Error processing",
                file_path.name,
                ":",
                error
            )

    if not results:
        raise RuntimeError(
            "No DEM tiles were successfully processed. "
            "No terrain report was created."
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nSuccessfully processed", len(results), "DEM tile(s).")
    print("Terrain feature report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()