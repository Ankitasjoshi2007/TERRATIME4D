import csv
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE = Path("data/processed/temporal_analysis/global")
TARGETS = BASE / "global_temporal_targets.csv"
CHECKPOINTS = BASE / "stac_checkpoints"

API = "https://earth-search.aws.element84.com/v1/search"

YEARS = list(range(2019, 2027))
MAX_PAGES = 10
WORKERS = 8
MAX_RETRIES = 4
TIMEOUT = 30

BASE.mkdir(parents=True, exist_ok=True)
CHECKPOINTS.mkdir(parents=True, exist_ok=True)

with TARGETS.open(encoding="utf-8-sig", newline="") as f:
    targets = list(csv.DictReader(f))


def save_checkpoint(path, data):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data), encoding="utf-8")
    temp.replace(path)


def deduplicate(features):
    unique = {}
    for item in features:
        key = item.get("id") or hashlib.sha1(
            json.dumps(item, sort_keys=True).encode()
        ).hexdigest()
        unique[key] = item
    return list(unique.values())


def search_target(target):
    tile = target["tile"]
    checkpoint = CHECKPOINTS / f"{tile}.json"

    old_features = []

    # Reuse old checkpoints without pretending they are verified.
    if checkpoint.exists():
        try:
            old = json.loads(checkpoint.read_text(encoding="utf-8"))

            if old.get("schema_version") == 2:
                old_features = old.get("features", [])

                if old.get("complete") is True:
                    return {
                        "tile": tile,
                        "features": old_features,
                        "status": "complete",
                    }

            elif isinstance(old.get("features"), list):
                return {
                    "tile": tile,
                    "features": old["features"],
                    "status": "legacy_unverified",
                }

        except Exception:
            print(f"Recovering empty/invalid checkpoint: {tile}")

    bbox = [
        float(target["west"]),
        float(target["south"]),
        float(target["east"]),
        float(target["north"]),
    ]

    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": "2019-01-01T00:00:00Z/2026-10-31T23:59:59Z",
        "query": {"eo:cloud_cover": {"lt": 40}},
        "limit": 100,
    }

    features = list(old_features)
    url = API
    method = "POST"
    body = payload
    complete = False
    error = ""
    pages_fetched = 0

    for page in range(MAX_PAGES):
        response = None

        for attempt in range(MAX_RETRIES):
            try:
                if method == "GET":
                    response = requests.get(
                        url, params=body, timeout=TIMEOUT
                    )
                else:
                    response = requests.post(
                        url, json=body, timeout=TIMEOUT
                    )

                if response.status_code in (429, 502, 503, 504):
                    time.sleep(2 ** attempt)
                    continue

                response.raise_for_status()
                break

            except requests.RequestException as exc:
                error = str(exc)
                time.sleep(2 ** attempt)

        if response is None or response.status_code in (
            429, 502, 503, 504
        ):
            error = error or "Request retries exhausted"
            break

        try:
            result = response.json()
        except ValueError:
            error = "Invalid JSON response"
            break

        features.extend(result.get("features", []))
        features = deduplicate(features)
        pages_fetched += 1

        next_link = next(
            (
                link for link in result.get("links", [])
                if link.get("rel") == "next"
            ),
            None,
        )

        if not next_link:
            complete = True
            error = ""
            break

        url = next_link["href"]
        method = next_link.get("method", "GET").upper()

        if method == "GET":
            body = next_link.get("merge", {})
        else:
            body = next_link.get("body", {})

    if not complete and not error:
        error = f"Pagination exceeded {MAX_PAGES} pages"

    data = {
        "schema_version": 2,
        "tile": tile,
        "features": features,
        "complete": complete,
        "status": "complete" if complete else "incomplete",
        "pages_fetched": pages_fetched,
        "error": error,
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    }

    save_checkpoint(checkpoint, data)

    return {
        "tile": tile,
        "features": features,
        "status": data["status"],
    }


print("TERRATIME4D GLOBAL SENTINEL-2 DISCOVERY")
print("Target tiles:", len(targets))
print("Workers:", WORKERS)
print("Old readable checkpoints will be preserved.")
print("Legacy results will be marked unverified.\n")

results = []
completed = 0

with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {
        pool.submit(search_target, target): target
        for target in targets
    }

    for future in as_completed(futures):
        target = futures[future]
        completed += 1

        try:
            result = future.result()
            results.append(result)

            print(
                f"[{completed}/{len(targets)}] "
                f"{target['tile']}: "
                f"{len(result['features'])} scenes "
                f"({result['status']})",
                flush=True,
            )

        except Exception as exc:
            print(
                f"[{completed}/{len(targets)}] "
                f"FAILED {target['tile']}: {exc}",
                flush=True,
            )

scene_rows = []
coverage_rows = []

for result in results:
    tile = result["tile"]
    status = result["status"]
    by_year_tile = {}

    for item in result["features"]:
        props = item.get("properties", {})
        dt = props.get("datetime", "")

        if not dt:
            continue

        year = int(dt[:4])

        if year not in YEARS:
            continue

        mgrs = (
            props.get("s2:mgrs_tile")
            or props.get("mgrs:tile")
            or item.get("id", "unknown")
        )

        cloud = props.get("eo:cloud_cover")
        key = (year, mgrs)

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
            coverage_status = (
                "OBSERVATIONS_FOUND" if selected else "NO_SCENE_FOUND"
            )
        else:
            coverage_status = (
                "OBSERVATIONS_FOUND_UNVERIFIED"
                if selected else "UNVERIFIED_NO_SCENE"
            )

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

complete_count = sum(
    r["status"] == "complete" for r in results
)
legacy_count = sum(
    r["status"] == "legacy_unverified" for r in results
)
incomplete_count = sum(
    r["status"] == "incomplete" for r in results
)

print("\nGLOBAL DISCOVERY RUN FINISHED")
print("Tiles represented:", len(results))
print("Verified complete:", complete_count)
print("Legacy unverified:", legacy_count)
print("Incomplete:", incomplete_count)
print("Selected scene records:", len(scene_rows))
print("Tile-year combinations:", len(coverage_rows))
print("Scene catalogue:", BASE / "global_sentinel_scene_catalogue.csv")
print("Coverage report:", BASE / "global_temporal_observation_coverage.csv")
print("Checkpoints:", CHECKPOINTS)
