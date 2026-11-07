
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "combined_earth_features.csv"
)


def load_earth_data():
    """Load the processed Earth terrain dataset."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Earth dataset not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    if "location" not in data.columns:
        raise ValueError(
            "Earth dataset must contain a 'location' column."
        )

    return data


def get_available_locations():
    """Return the names of available Earth locations."""
    data = load_earth_data()
    return data["location"].dropna().unique().tolist()


def get_location_features(location_name):
    """Return terrain features for a selected Earth location."""
    if not isinstance(location_name, str) or not location_name.strip():
        raise ValueError("Please provide a valid location name.")

    data = load_earth_data()

    selected = data[
        data["location"].astype(str).str.strip().str.casefold()
        == location_name.strip().casefold()
    ]

    if selected.empty:
        raise ValueError(f"Location not found: {location_name}")

    return selected.iloc[0].to_dict()


if __name__ == "__main__":
    earth_data = load_earth_data()

    print("TERRATIME 4D - EARTH DATA MODULE")
    print("--------------------------------")
    print("Available locations:")
    print(get_available_locations())

    print("\nDataset preview:")
    print(earth_data.head())

    if not earth_data.empty:
        first_location = get_available_locations()[0]
        print(f"\nFeatures for {first_location}:")
        print(get_location_features(first_location))
