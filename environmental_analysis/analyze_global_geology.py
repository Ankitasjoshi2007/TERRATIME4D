import csv
from pathlib import Path
from collections import Counter

BASE = Path("data/processed/global_geology_worldwide")
OUT = Path("data/processed/global_geology_analysis")
OUT.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

records = read_csv(BASE / "worldwide_geology_records.csv")
cells = read_csv(BASE / "worldwide_geology_cell_status.csv")

# 1. Geological period distribution
period_counts = Counter(
    r["geological_period"].strip()
    for r in records if r["geological_period"].strip()
)
period_rows = [
    {"geological_period": name, "record_count": count}
    for name, count in period_counts.most_common()
]
write_csv(
    OUT / "geological_period_distribution.csv",
    period_rows,
    ["geological_period", "record_count"]
)

# 2. Original lithology descriptions
lithology_counts = Counter(
    r["lithology"].strip()
    for r in records if r["lithology"].strip()
)
lithology_rows = [
    {"lithology": name, "record_count": count}
    for name, count in lithology_counts.most_common()
]
write_csv(
    OUT / "lithology_distribution.csv",
    lithology_rows,
    ["lithology", "record_count"]
)

# 3. Valid geological age intervals
age_rows = []
for r in records:
    try:
        a = float(r["top_age_ma"])
        b = float(r["bottom_age_ma"])
    except (ValueError, TypeError):
        continue

    younger = min(a, b)
    older = max(a, b)

    age_rows.append({
        "cell_id": r["cell_id"],
        "name": r["name"],
        "lithology": r["lithology"],
        "geological_period": r["geological_period"],
        "younger_age_ma": younger,
        "older_age_ma": older,
        "interval_duration_million_years": older - younger
    })

write_csv(
    OUT / "geological_age_intervals.csv",
    age_rows,
    [
        "cell_id", "name", "lithology", "geological_period",
        "younger_age_ma", "older_age_ma",
        "interval_duration_million_years"
    ]
)

# 4. Coverage summary for all 869 cells
actual_counts = Counter(r["cell_id"] for r in records)
cell_rows = []

for cell in cells:
    cell_id = cell["cell_id"]
    actual = actual_counts.get(cell_id, 0)
    reported = int(cell["record_count"])

    cell_rows.append({
        "cell_id": cell_id,
        "latitude": cell["latitude"],
        "longitude": cell["longitude"],
        "land_class": cell["land_class"],
        "collection_status": cell["status"],
        "reported_record_count": reported,
        "actual_record_count": actual,
        "has_geology_records": actual > 0,
        "count_matches": actual == reported
    })

write_csv(
    OUT / "global_geology_cell_coverage.csv",
    cell_rows,
    [
        "cell_id", "latitude", "longitude", "land_class",
        "collection_status", "reported_record_count",
        "actual_record_count", "has_geology_records", "count_matches"
    ]
)

# 5. Data quality summary
quality_rows = [{
    "total_records": len(records),
    "unique_cells_with_records": len(actual_counts),
    "total_grid_cells": len(cells),
    "cells_without_records": sum(v == 0 for v in actual_counts.values())
        + sum(c["cell_id"] not in actual_counts for c in cells),
    "records_with_valid_age_intervals": len(age_rows),
    "missing_lithology": sum(not r["lithology"].strip() for r in records),
    "missing_geological_period": sum(
        not r["geological_period"].strip() for r in records
    ),
    "reported_actual_count_mismatches": sum(
        not row["count_matches"] for row in cell_rows
    )
}]

write_csv(
    OUT / "global_geology_data_quality.csv",
    quality_rows,
    list(quality_rows[0].keys())
)

print("\nGLOBAL GEOLOGY ANALYSIS COMPLETE")
print("Input geological records:", len(records))
print("Grid cells:", len(cells))
print("Valid age intervals:", len(age_rows))
print("Distinct nonblank lithologies:", len(lithology_counts))
print("Distinct nonblank geological periods:", len(period_counts))
print("Cell count mismatches:",
      sum(not row["count_matches"] for row in cell_rows))
print("\nOutputs saved in:", OUT)
for p in sorted(OUT.glob("*.csv")):
    print("CREATED:", p.name)
