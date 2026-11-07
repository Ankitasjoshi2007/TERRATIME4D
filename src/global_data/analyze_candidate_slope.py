from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEM_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_geology_land_pilot"
    / "priority_candidate_locations.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "priority_candidate_slope_analysis.csv"
)

DEM_FILES = {
    "Western Australia": "Copernicus_DSM_COG_30_S33_00_E117_00_DEM.tif",
    "Queensland Australia": "Copernicus_DSM_COG_30_S23_00_E147_00_DEM.tif",
    "Baja California Mexico": "Copernicus_DSM_COG_30_N27_00_W113_00_DEM.tif",
    "Ontario Canada": "Copernicus_DSM_COG_30_N47_00_W083_00_DEM.tif",
    "Brooks Range Alaska": "Copernicus_DSM_COG_30_N67_00_W148_00_DEM.tif",
    "Scandinavia": "Copernicus_DSM_COG_30_N67_00_E017_00_DEM.tif",
}

WINDOW_SIZE = 101


def analyse_candidate(dataset, latitude, longitude):

    row, col = dataset.index(longitude, latitude)

    half = WINDOW_SIZE // 2

    row_start = max(0, row - half)
    col_start = max(0, col - half)

    row_end = min(dataset.height, row + half + 1)
    col_end = min(dataset.width, col + half + 1)

    window = Window(
        col_start,
        row_start,
        col_end - col_start,
        row_end - row_start
    )

    elevation = dataset.read(
        1,
        window=window,
        masked=True
    ).astype("float64")

    values = elevation.compressed()
    values = values[np.isfinite(values)]

    if len(values) == 0:
        raise ValueError("No valid elevation pixels found")

    # Convert pixel dimensions from degrees to approximate metres.
    center_latitude = latitude

    pixel_width_m = (
        abs(dataset.transform.a)
        * 111320
        * np.cos(np.radians(center_latitude))
    )

    pixel_height_m = abs(dataset.transform.e) * 111320

    # Calculate terrain gradients.
    elevation_array = elevation.filled(np.nan)

    gradient_y, gradient_x = np.gradient(
        elevation_array,
        pixel_height_m,
        pixel_width_m
    )

    slope = np.degrees(
        np.arctan(
            np.sqrt(gradient_x ** 2 + gradient_y ** 2)
        )
    )

    valid_slopes = slope[np.isfinite(slope)]

    if len(valid_slopes) == 0:
        raise ValueError("Unable to calculate valid slopes")

    return {
        "window_pixels": len(values),
        "elevation_min_m": round(float(values.min()), 2),
        "elevation_max_m": round(float(values.max()), 2),
        "elevation_range_m": round(
            float(values.max() - values.min()), 2
        ),
        "elevation_mean_m": round(float(values.mean()), 2),
        "slope_mean_degrees": round(float(valid_slopes.mean()), 2),
        "slope_median_degrees": round(float(np.median(valid_slopes)), 2),
        "slope_90th_percentile_degrees": round(
            float(np.percentile(valid_slopes, 90)), 2
        ),
        "slope_max_degrees": round(float(valid_slopes.max()), 2),
        "valid_slope_pixels": len(valid_slopes),
    }


def main():

    candidates = pd.read_csv(INPUT_FILE)

    results = []

    print("\nTERRATIME 4D - LOCAL TERRAIN SLOPE ANALYSIS")
    print("--------------------------------------------")

    for _, candidate in candidates.iterrows():

        location = candidate["location"]
        latitude = float(candidate["target_latitude"])
        longitude = float(candidate["target_longitude"])

        dem_name = DEM_FILES.get(location)

        if dem_name is None:
            print("\nNo DEM mapping:", location)
            continue

        dem_path = DEM_FOLDER / dem_name

        try:
            with rasterio.open(dem_path) as dataset:

                analysis = analyse_candidate(
                    dataset,
                    latitude,
                    longitude
                )

            result = {
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "dem_file": dem_name,
                **analysis,
                "status": "ANALYSED",
            }

            results.append(result)

            print("\nLocation:", location)
            print("Mean elevation:", analysis["elevation_mean_m"], "m")
            print("Elevation range:", analysis["elevation_range_m"], "m")
            print("Mean slope:", analysis["slope_mean_degrees"], "degrees")
            print(
                "90th percentile slope:",
                analysis["slope_90th_percentile_degrees"],
                "degrees"
            )
            print("Status: ANALYSED")

        except Exception as error:

            print("\nError:", location, error)

            results.append({
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "dem_file": dem_name,
                "status": "ERROR",
                "error": str(error),
            })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    successful = sum(
        result["status"] == "ANALYSED"
        for result in results
    )

    print("\nCandidates analysed:", successful, "/", len(candidates))
    print("\nReport saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()