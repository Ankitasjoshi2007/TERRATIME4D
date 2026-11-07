
from pathlib import Path
import shutil
import time

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PLAN_FILE = (
    PROJECT_ROOT / "data" / "processed" / "global_dem_plan"
    / "global_dem_download_plan.csv"
)

EXISTING_FOLDER = PROJECT_ROOT / "data" / "copernicus_glo90"
OUTPUT_FOLDER = Path(r"D:\TERRATIME4D_DEM")
REPORT_FILE = OUTPUT_FOLDER / "global_dem_download_status.csv"

BASE_URL = "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"
MAX_ATTEMPTS = 4
TIMEOUT = (20, 180)


def download_tile(session, tile_name):
    output_file = OUTPUT_FOLDER / f"{tile_name}.tif"
    temporary_file = OUTPUT_FOLDER / f"{tile_name}.tif.part"

    if output_file.exists() and output_file.stat().st_size > 0:
        return "Already on D:"

    # Reuse an existing project tile when it matches the global plan.
    existing_file = EXISTING_FOLDER / f"{tile_name}.tif"
    if existing_file.exists() and existing_file.stat().st_size > 0:
        shutil.copy2(existing_file, output_file)
        return "Copied existing tile"

    url = f"{BASE_URL}/{tile_name}/{tile_name}.tif"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with session.get(url, stream=True, timeout=TIMEOUT) as response:
                if response.status_code == 404:
                    return "Not available (404)"

                response.raise_for_status()

                with open(temporary_file, "wb") as file:
                    for chunk in response.iter_content(1024 * 1024):
                        if chunk:
                            file.write(chunk)

            if not temporary_file.exists() or temporary_file.stat().st_size == 0:
                raise IOError("Downloaded file is empty")

            temporary_file.replace(output_file)
            return "Downloaded"

        except (requests.RequestException, OSError) as error:
            if temporary_file.exists():
                temporary_file.unlink()

            print(f"Attempt {attempt}/{MAX_ATTEMPTS} failed for {tile_name}: {error}")

            if attempt < MAX_ATTEMPTS:
                time.sleep(2 * attempt)

    return "Failed"


def main():
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    if not PLAN_FILE.exists():
        raise FileNotFoundError(f"Global plan not found: {PLAN_FILE}")

    plan = pd.read_csv(PLAN_FILE)

    if "tile_name" not in plan.columns:
        raise ValueError("Global plan has no tile_name column")

    plan = plan.drop_duplicates(subset=["tile_name"]).copy()

    print("TERRATIME 4D — GLOBAL COPERNICUS GLO-90 DOWNLOAD")
    print("Unique planned tiles:", len(plan))
    print("Destination:", OUTPUT_FOLDER)

    results = []

    with requests.Session() as session:
        session.headers.update({"User-Agent": "TERRATIME4D-DEM-Collector/1.0"})

        for index, row in plan.iterrows():
            tile_name = str(row["tile_name"])
            print(f"\n[{len(results) + 1}/{len(plan)}] {tile_name}")

            status = download_tile(session, tile_name)
            print("Status:", status)

            result = row.to_dict()
            result["download_status"] = status
            results.append(result)

            # Save progress after every tile, so the run can be resumed.
            pd.DataFrame(results).to_csv(REPORT_FILE, index=False)

    report = pd.DataFrame(results)

    print("\nDOWNLOAD SUMMARY")
    print(report["download_status"].value_counts().to_string())
    print("\nReport saved to:", REPORT_FILE)
    print("Download operation finished. Review unavailable and failed tiles.")


if __name__ == "__main__":
    main()
