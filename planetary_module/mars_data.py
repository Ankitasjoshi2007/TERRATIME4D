from pathlib import Path

# Project data folder
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Raw Mars data folder
MARS_DATA_DIR = DATA_DIR / "raw" / "mars"


def get_mars_data_files():
    """Find available files in the raw Mars data folder."""
    if not MARS_DATA_DIR.exists():
        return []

    return [
        file for file in MARS_DATA_DIR.rglob("*")
        if file.is_file()
    ]


if __name__ == "__main__":
    files = get_mars_data_files()

    print("Mars data folder:", MARS_DATA_DIR)
    print("Number of files found:", len(files))

    for file in files:
        print(file.name)