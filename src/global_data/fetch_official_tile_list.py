
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "copernicus_glo90_tileList.txt"
)

URL = (
    "https://copernicus-dem-90m.s3.amazonaws.com/tileList.txt"
)


def main():
    print("\nTERRATIME 4D - OFFICIAL GLO-90 TILE LIST")
    print("----------------------------------------")

    response = requests.get(URL, timeout=60)
    response.raise_for_status()

    content = response.text

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        content,
        encoding="utf-8"
    )

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    print("Metadata file downloaded successfully.")
    print("Number of entries:", len(lines))
    print("\nFirst 10 entries:")

    for line in lines[:10]:
        print(line)

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
