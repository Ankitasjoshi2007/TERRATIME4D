from pathlib import Path

# Project data folder
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Raw Moon data folder
MOON_DATA_DIR = DATA_DIR / "raw" / "moon"


def get_moon_data_files():
    """Find available files in the raw Moon data folder."""
    if not MOON_DATA_DIR.exists():
        return []

    return [
        file for file in MOON_DATA_DIR.rglob("*")
        if file.is_file()
    ]


if __name__ == "__main__":
    files = get_moon_data_files()

    print("Moon data folder:", MOON_DATA_DIR)
    print("Number of files found:", len(files))

    for file in files:
        print(file.name)