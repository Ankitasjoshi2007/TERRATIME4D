from pathlib import Path

import pandas as pd
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "global_geology_land_pilot"
    / "priority_candidate_locations.csv"
)

DEM_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "priority_candidate_elevations.csv"
)


DEM_FILES = {
    "Western Australia": "Copernicus_DSM_COG_30_S33_00_E117_00_DEM.tif",
    "Queensland Australia": "Copernicus_DSM_COG_30_S23_00_E147_00_DEM.tif",
    "Baja California Mexico": "Copernicus_DSM_COG_30_N27_00_W113_00_DEM.tif",
    "Ontario Canada": "Copernicus_DSM_COG_30_N47_00_W083_00_DEM.tif",
    "Brooks Range Alaska": "Copernicus_DSM_COG_30_N67_00_W148_00_DEM.tif",
    "Scandinavia": "Copernicus_DSM_COG_30_N67_00_E017_00_DEM.tif",
}


def main():

    candidates = pd.read_csv(INPUT_FILE)

    results = []

    print("\nTERRATIME 4D - CANDIDATE ELEVATION SAMPLING")
    print("--------------------------------------------")

    for _, candidate in candidates.iterrows():

        location = candidate["location"]
        latitude = float(candidate["target_latitude"])
        longitude = float(candidate["target_longitude"])

        dem_name = DEM_FILES.get(location)

        if dem_name is None:
            print("\nNo DEM mapping found:", location)
            continue

        dem_path = DEM_FOLDER / dem_name

        if not dem_path.exists():
            print("\nDEM file missing:", dem_name)
            continue

        try:
            with rasterio.open(dem_path) as dataset:

                sampled = next(
                    dataset.sample([(longitude, latitude)])
                )

                elevation = float(sampled[0])

                row = {
                    "location": location,
                    "latitude": latitude,
                    "longitude": longitude,
                    "elevation_m": round(elevation, 2),
                    "dem_file": dem_name,
                    "status": "SAMPLED",
                }

                results.append(row)

                print("\nLocation:", location)
                print("Coordinates:", latitude, longitude)
                print("Elevation:", round(elevation, 2), "metres")
                print("Status: SAMPLED")

        except Exception as error:

            print("\nError:", location, error)

            results.append({
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "elevation_m": None,
                "dem_file": dem_name,
                "status": "ERROR",
            })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nResults saved to:")
    print(OUTPUT_FILE)

    print("\nCandidates sampled:", len(results))


if __name__ == "__main__":
    main()