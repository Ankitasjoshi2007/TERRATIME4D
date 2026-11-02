from pathlib import Path
import math
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = PROJECT_ROOT / "data" / "processed"


def create_tile_name(latitude, longitude):
    lat = math.floor(latitude)
    lon = math.floor(longitude)

    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"

    return (
        f"Copernicus_DSM_COG_30_"
        f"{ns}{abs(lat):02d}_00_"
        f"{ew}{abs(lon):03d}_00_DEM"
    )


def main():
    elevation = pd.read_csv(
        PROCESSED / "srtm_elevation_summary.csv"
    )

    slope = pd.read_csv(
        PROCESSED / "global_terrain_features.csv"
    )

    roughness = pd.read_csv(
        PROCESSED / "global_roughness_summary.csv"
    )

    locations = pd.read_csv(
        PROCESSED / "global_sample_locations.csv"
    )

    # Match all reports using the DEM tile name.
    elevation["tile"] = elevation["file"].str.replace(
        ".hgt", "", regex=False
    )

    slope["tile"] = slope["location_tile"]
    roughness["tile"] = roughness["tile"]

    # Add location coordinates and tile names.
    locations["tile"] = locations.apply(
        lambda row: create_tile_name(
            row["target_latitude"],
            row["target_longitude"]
        ),
        axis=1
    )

    # Combine the terrain reports.
    combined = slope.merge(
        roughness,
        on="tile",
        how="left",
        suffixes=("_slope", "_roughness")
    )

    # Add location information.
    combined = combined.merge(
        locations[
            ["tile", "location", "target_latitude", "target_longitude"]
        ],
        on="tile",
        how="left"
    )

    output_file = PROCESSED / "combined_earth_features.csv"
    combined.to_csv(output_file, index=False)

    print("\nTERRATIME 4D - COMBINED EARTH DATA")
    print("---------------------------------")
    print("Locations combined:", len(combined))
    print("\n", combined.to_string(index=False))
    print("\nSaved to:", output_file)


if __name__ == "__main__":
    main()