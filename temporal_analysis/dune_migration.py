from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime
import csv
import json
import time

PROJECT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT / "data" / "processed" / "temporal_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STAC_URL = "https://earth-search.aws.element84.com/v1/search"
COLLECTION = "sentinel-2-l2a"

BBOX = [14.7, -25.0, 15.5, -24.3]

START_DATE = "2017-01-01T00:00:00Z"
END_DATE = "2026-10-31T23:59:59Z"

MAX_CLOUD = 30
SEASON_MONTHS = [6, 7, 8, 9]

CATALOGUE_CSV = OUTPUT_DIR / "namib_sentinel2_scene_catalogue.csv"
SELECTED_CSV = OUTPUT_DIR / "namib_selected_scenes_by_year.csv"
CHECKPOINT = OUTPUT_DIR / "namib_search_checkpoint.json"


def save_checkpoint(features, next_request):
    temporary = CHECKPOINT.with_suffix(".tmp")

    with open(temporary, "w", encoding="utf-8") as file:
        json.dump(
            {
                "features": features,
                "next_request": next_request
            },
            file
        )

    temporary.replace(CHECKPOINT)


def fetch_page(method, url, payload=None, retries=6):
    for attempt in range(retries):
        try:
            data = None

            headers = {
                "Accept": "application/geo+json",
                "User-Agent": "TERRATIME4D/1.0"
            }

            if method.upper() == "POST":
                data = json.dumps(payload or {}).encode("utf-8")
                headers["Content-Type"] = "application/json"

            request = Request(
                url,
                data=data,
                headers=headers,
                method=method.upper()
            )

            with urlopen(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504):
                raise

            wait = min(10 * (2 ** attempt), 60)

            print(
                f"HTTP {error.code}: retry "
                f"{attempt + 1}/{retries} in {wait}s"
            )

            if attempt == retries - 1:
                raise

            time.sleep(wait)

        except (URLError, TimeoutError) as error:
            wait = min(10 * (2 ** attempt), 60)

            print(
                f"Connection error ({error}): retry "
                f"{attempt + 1}/{retries} in {wait}s"
            )

            if attempt == retries - 1:
                raise

            time.sleep(wait)


def search_scenes():
    if CHECKPOINT.exists():
        print("Loading saved catalogue checkpoint...")

        with open(CHECKPOINT, "r", encoding="utf-8") as file:
            saved = json.load(file)

        features = saved.get("features", [])
        next_request = saved.get("next_request")

        print(f"Previously saved scenes: {len(features)}")

    else:
        features = []

        payload = {
            "collections": [COLLECTION],
            "bbox": BBOX,
            "datetime": f"{START_DATE}/{END_DATE}",
            "limit": 100
        }

        next_request = {
            "method": "POST",
            "url": STAC_URL,
            "payload": payload
        }

    known_ids = {
        feature.get("id")
        for feature in features
    }

    page_number = 0

    while next_request:
        page_number += 1

        try:
            result = fetch_page(
                next_request["method"],
                next_request["url"],
                next_request.get("payload")
            )

        except Exception as error:
            print(f"\nCatalogue request failed: {error}")
            print("Stopping catalogue retrieval safely.")
            print(f"Processing {len(features)} saved scenes instead.")

            # Preserve the failed next-page request for later resumption.
            save_checkpoint(features, next_request)
            break

        page_features = result.get("features", [])
        added = 0

        for feature in page_features:
            feature_id = feature.get("id")

            if feature_id not in known_ids:
                features.append(feature)
                known_ids.add(feature_id)
                added += 1

        print(
            f"Page {page_number}: {len(page_features)} scenes | "
            f"New: {added} | Total: {len(features)}"
        )

        next_link = next(
            (
                link for link in result.get("links", [])
                if link.get("rel") == "next"
            ),
            None
        )

        if next_link:
            next_request = {
                "method": next_link.get("method", "GET").upper(),
                "url": next_link["href"],
                "payload": next_link.get("body")
            }
        else:
            next_request = None

        save_checkpoint(features, next_request)

    if next_request is None and CHECKPOINT.exists():
        CHECKPOINT.unlink()
        print("Catalogue retrieval completed; checkpoint closed.")

    return features


def get_scene_details(feature):
    properties = feature.get("properties", {})

    scene_datetime = properties.get("datetime")
    cloud_cover = properties.get("eo:cloud_cover")

    try:
        parsed_datetime = datetime.fromisoformat(
            scene_datetime.replace("Z", "+00:00")
        )
    except (ValueError, AttributeError):
        return None

    return {
        "scene_id": feature.get("id", ""),
        "datetime": scene_datetime,
        "year": parsed_datetime.year,
        "month": parsed_datetime.month,
        "cloud_cover": cloud_cover,
        "platform": properties.get("platform", ""),
        "collection": COLLECTION
    }


def save_csv(path, rows):
    if not rows:
        print(f"No records to save: {path}")
        return

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved: {path}")


def main():
    print("\nTERRATIME4D - DUNE MIGRATION PILOT")
    print("=" * 55)
    print("Study area: Namib Sand Sea, Namibia")
    print("Season: June to September")
    print(f"Cloud cover limit: {MAX_CLOUD}%")
    print()

    features = search_scenes()

    print("\nCATALOGUE RESULTS")
    print("=" * 55)
    print(f"Total unique scenes retrieved: {len(features)}")

    all_scenes = []
    candidates = []

    for feature in features:
        scene = get_scene_details(feature)

        if scene is None:
            continue

        all_scenes.append(scene)

        cloud = scene["cloud_cover"]

        if (
            scene["month"] in SEASON_MONTHS
            and cloud is not None
            and cloud <= MAX_CLOUD
        ):
            candidates.append(scene)

    all_scenes.sort(key=lambda item: item["datetime"])
    candidates.sort(key=lambda item: item["datetime"])

    save_csv(CATALOGUE_CSV, all_scenes)

    candidates_by_year = {}

    for scene in candidates:
        candidates_by_year.setdefault(
            scene["year"], []
        ).append(scene)

    print("\nAVAILABLE CANDIDATES BY YEAR")
    print("-" * 55)

    for year in sorted(candidates_by_year):
        print(f"{year}: {len(candidates_by_year[year])} scenes")

    selected = []

    for year, year_scenes in sorted(candidates_by_year.items()):
        clearest = min(
            year_scenes,
            key=lambda item: item["cloud_cover"]
        )
        selected.append(clearest)

    save_csv(SELECTED_CSV, selected)

    print("\nSELECTED SCENES")
    print("-" * 55)

    for scene in selected:
        print(
            f"{scene['year']} | {scene['datetime']} | "
            f"Cloud: {scene['cloud_cover']}%"
        )

    print("\nSUMMARY")
    print("=" * 55)
    print(f"Total scenes: {len(features)}")
    print(f"Seasonal low-cloud candidates: {len(candidates)}")
    print(f"Years represented: {len(selected)}")

    if len(selected) < 2:
        print("WARNING: Fewer than two suitable years found.")
    else:
        print("SUCCESS: Multiple years available for temporal analysis.")

    if CHECKPOINT.exists():
        print("\nNOTE: Checkpoint retained for later catalogue resumption.")

    print("\nNext stage: imagery download and dune migration measurement.")


if __name__ == "__main__":
    main()
PY