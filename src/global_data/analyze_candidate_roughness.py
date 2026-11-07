from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import generic_filter
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
    / "priority_candidate_roughness_analysis.csv"
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


def local_roughness(values):

    valid = values[np.isfinite(values)]

    if valid.size < 5:
        return np.nan

    return float(np.std(valid))


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

    elevation = elevation.filled(np.nan)

    valid_mask = np.isfinite(elevation)

    if not np.any(valid_mask):
        raise ValueError("No valid elevation pixels found")

    roughness = generic_filter(
        elevation,
        local_roughness,
        size=3,
        mode="constant",
        cval=np.nan
    )

    roughness_values = roughness[
        valid_mask & np.isfinite(roughness)
    ]

    if roughness_values.size == 0:
        raise ValueError("No valid roughness values calculated")

    return {
        "valid_elevation_pixels": int(valid_mask.sum()),
        "valid_roughness_pixels": int(roughness_values.size),
        "roughness_mean_m": round(
            float(roughness_values.mean()), 2
        ),
        "roughness_median_m": round(
            float(np.median(roughness_values)), 2
        ),
        "roughness_90th_percentile_m": round(
            float(np.percentile(roughness_values, 90)), 2
        ),
        "roughness_max_m": round(
            float(roughness_values.max()), 2
        ),
    }


def main():

    candidates = pd.read_csv(INPUT_FILE)

    results = []

    print("\nTERRATIME 4D - CANDIDATE TERRAIN ROUGHNESS")
    print("-------------------------------------------")

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
                "status": "ANALYSED"
            }

            results.append(result)

            print("\nLocation:", location)
            print(
                "Mean roughness:",
                analysis["roughness_mean_m"],
                "metres"
            )
            print(
                "90th percentile roughness:",
                analysis["roughness_90th_percentile_m"],
                "metres"
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
                "error": str(error)
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