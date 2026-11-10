import csv
import json
from pathlib import Path

BASE = Path("data/processed/temporal_analysis/global")
CHECKPOINTS = BASE / "stac_checkpoints"
TARGETS = BASE / "global_temporal_targets.csv"
YEARS = range(2019, 2027)

with TARGETS.open(encoding="utf-8-sig", newline="") as f:
    targets = list(csv.DictReader(f))

scene_rows = []
coverage_rows = []
counts = {
    "complete": 0,
    "legacy_unverified": 0,
    "incomplete": 0,
    "missing": 0,
    "invalid": 0,
}

for target in targets:
    tile = target["tile"]
    path = CHECKPOINTS / f"{tile}.json"

    if not path.exists():
        status, features = "missing", []
        counts["missing"] += 1
    else:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            if not isinstance(data, dict):
                raise ValueError("Invalid checkpoint structure")

            features = data.get("features", [])

            if not isinstance(features, list):
                raise ValueError("Invalid features list")

            if data.get("schema_version") == 2:
                status = "complete" if data.get("complete") is True else "incomplete"
            else:
                status = "legacy_unverified"

            counts[status] += 1

        except Exception:
            status, features = "invalid", []
            counts["invalid"] += 1

    by_year_tile = {}

    for item in features:
        props = item.get("properties", {})
        dt = props.get("datetime", "")

        try:
            year = int(dt[:4])
        except (ValueError, TypeError):
            continue

        if year not in YEARS:
            continue

        mgrs = (
            props.get("s2:mgrs_tile")
            or props.get("mgrs:tile")
            or item.get("id", "unknown")
        )

        cloud = props.get("eo:cloud_cover")

        row = {
            "dem_tile": tile,
            "year": year,
            "scene_id": item.get("id", ""),
            "datetime": dt,
            "mgrs_tile": mgrs,
            "cloud_cover": cloud,
            "platform": props.get("platform", ""),
            "red_href": item.get("assets", {}).get("red", {}).get("href", ""),
            "nir_href": item.get("assets", {}).get("nir", {}).get("href", ""),
            "scl_href": item.get("assets", {}).get("scl", {}).get("href", ""),
            "discovery_status": status,
        }

        key = (year, mgrs)
        old = by_year_tile.get(key)

        if old is None or (
            cloud if cloud is not None else 100
        ) < (
            old["cloud_cover"] if old["cloud_cover"] is not None else 100
        ):
            by_year_tile[key] = row

    scene_rows.extend(by_year_tile.values())

    for year in YEARS:
        selected = [
            row for row in by_year_tile.values()
            if row["year"] == year
        ]

        if status == "complete":
            coverage_status = "OBSERVATIONS_FOUND" if selected else "NO_SCENE_FOUND"
        elif status == "legacy_unverified":
            coverage_status = "OBSERVATIONS_FOUND_UNVERIFIED" if selected else "UNVERIFIED_NO_SCENE"
        elif status == "incomplete":
            coverage_status = "INCOMPLETE_DISCOVERY"
        elif status == "missing":
            coverage_status = "CHECKPOINT_MISSING"
        else:
            coverage_status = "INVALID_CHECKPOINT"

        coverage_rows.append({
            "dem_tile": tile,
            "year": year,
            "selected_scene_count": len(selected),
            "status": coverage_status,
            "discovery_status": status,
        })

def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

write_csv(
    BASE / "global_sentinel_scene_catalogue.csv",
    scene_rows,
    [
        "dem_tile", "year", "scene_id", "datetime",
        "mgrs_tile", "cloud_cover", "platform",
        "red_href", "nir_href", "scl_href",
        "discovery_status",
    ],
)

write_csv(
    BASE / "global_temporal_observation_coverage.csv",
    coverage_rows,
    [
        "dem_tile", "year", "selected_scene_count",
        "status", "discovery_status",
    ],
)

print("\nGLOBAL SENTINEL CHECKPOINT RECOVERY")
print("Target tiles:", len(targets))
print("Checkpoint status:", counts)
print("Scene records:", len(scene_rows))
print("Tile-year records:", len(coverage_rows))
print("Catalogue:", BASE / "global_sentinel_scene_catalogue.csv")
print("Coverage:", BASE / "global_temporal_observation_coverage.csv")
