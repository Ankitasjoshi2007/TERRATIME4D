
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
    """
    Load the processed Earth terrain dataset.
    Returns a pandas DataFrame.
    """
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Earth dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


def get_available_locations():
    """
    Return the names of locations in the Earth dataset.
    """
    data = load_earth_data()
    return data["location"].dropna().tolist()


if __name__ == "__main__":
    earth_data = load_earth_data()

    print("TERRATIME 4D - EARTH DATA MODULE")
    print("--------------------------------")
    print("Available locations:")
    print(get_available_locations())

    print("\nDataset preview:")
    print(earth_data.head())
