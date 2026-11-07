from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = PROJECT_ROOT / "data" / "processed"

INPUT_FILES = {
    "elevation": PROCESSED / "priority_candidate_elevations.csv",
    "slope": PROCESSED / "priority_candidate_slope_analysis.csv",
    "roughness": PROCESSED / "priority_candidate_roughness_analysis.csv",
}

OUTPUT_FILE = (
    PROCESSED / "combined_priority_candidate_terrain.csv"
)


def main():

    datasets = {}

    for name, file_path in INPUT_FILES.items():

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing {name} file: {file_path}"
            )

        datasets[name] = pd.read_csv(file_path)

    # Check that each dataset contains the expected columns.
    required_columns = {
        "elevation": {
            "location", "latitude", "longitude",
            "elevation_m", "status"
        },
        "slope": {
            "location", "latitude", "longitude",
            "slope_mean_degrees",
            "slope_median_degrees",
            "slope_90th_percentile_degrees",
            "slope_max_degrees",
            "status"
        },
        "roughness": {
            "location", "latitude", "longitude",
            "roughness_mean_m",
            "roughness_median_m",
            "roughness_90th_percentile_m",
            "roughness_max_m",
            "status"
        },
    }

    for name, dataframe in datasets.items():

        missing = required_columns[name] - set(dataframe.columns)

        if missing:
            raise ValueError(
                f"{name} dataset is missing columns: "
                f"{sorted(missing)}"
            )

        if dataframe["location"].duplicated().any():
            raise ValueError(
                f"Duplicate locations found in {name} dataset."
            )

        if not (dataframe["status"] == (
            "SAMPLED" if name == "elevation" else "ANALYSED"
        )).all():
            raise ValueError(
                f"Some records in {name} dataset were unsuccessful."
            )

    # Check that all datasets contain the same six candidates.
    reference_locations = set(
        datasets["elevation"]["location"]
    )

    for name, dataframe in datasets.items():

        if set(dataframe["location"]) != reference_locations:
            raise ValueError(
                f"Candidate locations do not match in {name} dataset."
            )

    # Check that candidate coordinates match.
    for name in ("slope", "roughness"):

        comparison = datasets["elevation"][
            ["location", "latitude", "longitude"]
        ].merge(
            datasets[name][
                ["location", "latitude", "longitude"]
            ],
            on="location",
            suffixes=("_elevation", "_other"),
            validate="one_to_one"
        )

        if not (
            comparison["latitude_elevation"].equals(
                comparison["latitude_other"]
            )
            and comparison["longitude_elevation"].equals(
                comparison["longitude_other"]
            )
        ):
            raise ValueError(
                f"Coordinate mismatch found in {name} dataset."
            )

    # Select the required measurements.
    elevation = datasets["elevation"][
        ["location", "latitude", "longitude", "elevation_m"]
    ]

    slope = datasets["slope"][
        [
            "location",
            "slope_mean_degrees",
            "slope_median_degrees",
            "slope_90th_percentile_degrees",
            "slope_max_degrees",
        ]
    ]

    roughness = datasets["roughness"][
        [
            "location",
            "roughness_mean_m",
            "roughness_median_m",
            "roughness_90th_percentile_m",
            "roughness_max_m",
        ]
    ]

    # Combine all three datasets.
    combined = elevation.merge(
        slope,
        on="location",
        how="inner",
        validate="one_to_one"
    )

    combined = combined.merge(
        roughness,
        on="location",
        how="inner",
        validate="one_to_one"
    )

    if len(combined) != len(reference_locations):
        raise ValueError(
            "The combined dataset does not contain all candidates."
        )

    # Keep the original candidate order.
    combined["candidate_order"] = combined["location"].map(
        {
            location: index
            for index, location in enumerate(
                datasets["elevation"]["location"]
            )
        }
    )

    combined = (
        combined
        .sort_values("candidate_order")
        .drop(columns=["candidate_order"])
        .reset_index(drop=True)
    )

    PROCESSED.mkdir(
        parents=True,
        exist_ok=True
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nTERRATIME 4D - PRIORITY CANDIDATE TERRAIN DATA")
    print("-----------------------------------------------")
    print("Candidates combined:", len(combined))

    print("\nCombined terrain dataset:")
    print(combined.to_string(index=False))

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()