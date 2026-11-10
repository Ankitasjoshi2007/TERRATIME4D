from pathlib import Path
from collections import defaultdict
import argparse
import csv
import shutil
import tempfile
import zipfile

import pandas as pd
import advanced_terrain as terrain


PROJECT = Path(__file__).resolve().parents[1]
ARCHIVE_FOLDER = PROJECT.parent

ARCHIVES = sorted(
    ARCHIVE_FOLDER.glob("TERRATIME4D_DEM*.zip")
)

OUTPUT_ROOT = PROJECT / "data" / "processed" / "global_terrain"
RASTER_OUTPUT = OUTPUT_ROOT / "advanced_rasters"
SUMMARY_FILE = OUTPUT_ROOT / "global_advanced_terrain_summary.csv"
FINGERPRINT_FILE = OUTPUT_ROOT / "global_terrain_fingerprints.csv"
LOG_FILE = OUTPUT_ROOT / "global_processing_log.csv"


def build_inventory():
    inventory = defaultdict(list)

    for archive in ARCHIVES:
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue

                if not info.filename.lower().endswith((".tif", ".tiff")):
                    continue

                inventory[Path(info.filename).name.lower()].append(
                    (archive, info)
                )

    selected = []
    conflicts = []

    for filename, entries in sorted(inventory.items()):
        signatures = {
            (info.CRC, info.file_size)
            for _, info in entries
        }

        if len(signatures) > 1:
            conflicts.append({
                "filename": filename,
                "status": "CONFLICTING_DUPLICATES",
                "copies": len(entries)
            })
            continue

        selected.append((filename, entries[0][0], entries[0][1]))

    return selected, conflicts, inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Maximum number of new tiles to process; 1 for initial test"
    )
    parser.add_argument(
        "--rebuild-all",
        action="store_true",
        help="Reprocess every selected DEM, including existing rasters"
    )
    args = parser.parse_args()

    if not ARCHIVES:
        raise FileNotFoundError(
            f"No TERRATIME4D_DEM ZIP archives found in {ARCHIVE_FOLDER}"
        )

    RASTER_OUTPUT.mkdir(parents=True, exist_ok=True)

    selected, conflicts, inventory = build_inventory()

    print("\nTERRATIME 4D - GLOBAL ADVANCED TERRAIN PIPELINE")
    print("=" * 65)
    print("Archives:", len(ARCHIVES))
    print("Unique filenames:", len(inventory))
    print("Non-conflicting unique tiles:", len(selected))
    print("Conflicting duplicate filenames:", len(conflicts))

    terrain.OUTPUT_FOLDER = RASTER_OUTPUT
    terrain.INPUT_FOLDER = RASTER_OUTPUT
    terrain.SUMMARY_FILE = SUMMARY_FILE
    terrain.FINGERPRINT_FILE = FINGERPRINT_FILE

    old_get_location = terrain.get_location
    terrain.get_location = lambda filename: Path(filename).stem

    summaries = []
    fingerprints = []
    logs = []

    if SUMMARY_FILE.exists():
        summaries = pd.read_csv(SUMMARY_FILE).to_dict("records")

    if FINGERPRINT_FILE.exists():
        fingerprints = pd.read_csv(FINGERPRINT_FILE).to_dict("records")

    completed = {
        row.get("raster_file")
        for row in summaries
        if row.get("raster_file")
    }

    if args.rebuild_all:
        pending = selected
    else:
        pending = [
            item for item in selected
            if item[0].removesuffix(".tif").removesuffix(".tiff")
            not in completed
            and not (
                RASTER_OUTPUT /
                f"{Path(item[0]).stem}_advanced_terrain.tif"
            ).exists()
        ]

    print("Already completed:", len(completed))
    print("Tiles remaining:", len(pending))

    if args.limit < 1:
        raise ValueError("--limit must be at least 1")

    batch = pending[:args.limit]

    for index, (filename, archive, info) in enumerate(batch, start=1):
        print(f"\n[{index}/{len(batch)}] Processing: {filename}")

        try:
            with tempfile.TemporaryDirectory(prefix="terratime_tile_") as tmp:
                temporary_dem = Path(tmp) / Path(filename).name

                with zipfile.ZipFile(archive) as z:
                    with z.open(info) as source:
                        with temporary_dem.open("wb") as destination:
                            shutil.copyfileobj(source, destination)

                summary, fingerprint = terrain.analyze_raster(
                    temporary_dem
                )

                # Replace previous records for this tile, not duplicate them.
                tile_key = summary.get("raster_file") or summary.get("location")
                summaries = [
                    row for row in summaries
                    if (row.get("raster_file") or row.get("location")) != tile_key
                ]

                fingerprint_key = (
                    fingerprint.get("raster_file")
                    or fingerprint.get("location")
                )
                fingerprints = [
                    row for row in fingerprints
                    if (row.get("raster_file") or row.get("location"))
                    != fingerprint_key
                ]

                summaries.append(summary)
                fingerprints.append(fingerprint)

                logs.append({
                    "filename": filename,
                    "archive": archive.name,
                    "status": "SUCCESS",
                    "error": ""
                })

        except Exception as error:
            print("FAILED:", error)

            logs.append({
                "filename": filename,
                "archive": archive.name,
                "status": "FAILED",
                "error": str(error)
            })

        pd.DataFrame(summaries).to_csv(SUMMARY_FILE, index=False)
        pd.DataFrame(fingerprints).to_csv(FINGERPRINT_FILE, index=False)

    conflict_rows = [
        {
            "filename": item["filename"],
            "archive": "",
            "status": item["status"],
            "error": f"{item['copies']} copies have different CRC/size"
        }
        for item in conflicts
    ]

    if LOG_FILE.exists():
        old_logs = pd.read_csv(LOG_FILE).to_dict("records")
    else:
        old_logs = []

    combined_logs = old_logs + logs + conflict_rows
    pd.DataFrame(combined_logs).drop_duplicates(
        subset=["filename", "status", "archive"],
        keep="last"
    ).to_csv(LOG_FILE, index=False)

    print("\n" + "=" * 65)
    print("BATCH FINISHED")
    print("Successful tiles in summary:", len(summaries))
    print("Advanced rasters:", RASTER_OUTPUT)
    print("Summary:", SUMMARY_FILE)
    print("Fingerprint:", FINGERPRINT_FILE)
    print("Processing log:", LOG_FILE)

    terrain.get_location = old_get_location


if __name__ == "__main__":
    main()
