
from pathlib import Path
import math
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED / "combined_earth_features.csv"


def create_tile_name(latitude, longitude):
    """Create a Copernicus tile name from latitude and longitude."""

    lat = math.floor(float(latitude))
    lon = math.floor(float(longitude))

    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"

    return (
        f"Copernicus_DSM_COG_30_"
        f"{ns}{abs(lat):02d}_00_"
        f"{ew}{abs(lon):03d}_00_DEM"
    )


def main():
    required_files = {
        "terrain": PROCESSED / "global_terrain_features.csv",
        "roughness": PROCESSED / "global_roughness_summary.csv",
        "locations": PROCESSED / "global_sample_locations.csv",
    }

    for name, file_path in required_files.items():
        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing {name} file: {file_path}"
            )

    terrain = pd.read_csv(required_files["terrain"])
    roughness = pd.read_csv(required_files["roughness"])
    locations = pd.read_csv(required_files["locations"])

    # Validate required columns.
    required_columns = {
        "terrain": {"location_tile", "average_elevation_m",
                    "average_slope_degrees"},
        "roughness": {"tile", "average_roughness_m"},
        "locations": {"location", "target_latitude",
                      "target_longitude"},
    }

    datasets = {
        "terrain": terrain,
        "roughness": roughness,
        "locations": locations,
    }

    for name, columns in required_columns.items():
        missing = columns - set(datasets[name].columns)

        if missing:
            raise ValueError(
                f"{name} dataset is missing columns: {sorted(missing)}"
            )

    # Standardize tile identifiers.
    terrain["tile"] = terrain["location_tile"].astype(str).str.strip()
    roughness["tile"] = roughness["tile"].astype(str).str.strip()

    locations["tile"] = locations.apply(
        lambda row: create_tile_name(
            row["target_latitude"],
            row["target_longitude"]
        ),
        axis=1
    )

    # Prevent accidental duplicate matches.
    for name, dataframe in datasets.items():
        if name == "locations":
            key = "tile"
        elif name == "terrain":
            key = "location_tile"
        else:
            key = "tile"

        if dataframe[key].duplicated().any():
            raise ValueError(
                f"Duplicate tile identifiers found in {name} dataset."
            )

    terrain_data = terrain.merge(
        roughness,
        on="tile",
        how="left",
        validate="one_to_one",
        suffixes=("_terrain", "_roughness")
    )

    combined = terrain_data.merge(
        locations[
            ["tile", "location", "target_latitude",
             "target_longitude"]
        ],
        on="tile",
        how="left",
        validate="one_to_one",
        indicator=True
    )

    unmatched = combined[combined["_merge"] != "both"]

    if not unmatched.empty:
        raise ValueError(
            "Some terrain tiles could not be matched to locations: "
            + ", ".join(unmatched["tile"].tolist())
        )

    combined = combined.drop(columns=["_merge"])

    if combined["average_roughness_m"].isna().any():
        raise ValueError(
            "Some terrain tiles are missing roughness measurements."
        )

    # Save combined Earth features.
    PROCESSED.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    print("\nTERRATIME 4D - COMBINED EARTH DATA")
    print("---------------------------------")
    print("Locations combined:", len(combined))
    print("\nCombined dataset:")
    print(combined.to_string(index=False))
    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
