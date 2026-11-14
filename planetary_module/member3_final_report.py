
from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parent.parent

ANALYSIS_DIR = ROOT / "results" / "member3_global_analysis_v3"
COMPARISON_DIR = ROOT / "results" / "member3_global_comparison_v3"
OUTPUT_DIR = ROOT / "results" / "MEMBER3_FINAL"

EARTH_AUDIT_FILE = ANALYSIS_DIR / "earth_reference_audit_v3.csv"
PLANETARY_SUMMARY_FILE = ANALYSIS_DIR / "moon_mars_physical_summary_v3.csv"
COMPARISON_REPORT_FILE = (
    COMPARISON_DIR / "member3_planetary_comparison_report_v3.txt"
)
ANALOGY_REPORT_FILE = (
    ROOT / "results" / "member3_final_analysis"
    / "member3_analogy_assessment.md"
)

OUTPUT_FILE = OUTPUT_DIR / "MEMBER3_FINAL_REPORT.md"


def read_csv_rows(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def number(row, column):
    value = row.get(column, "")
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing value for required column: {column}")
    return float(value)


def format_number(value, decimals=4):
    return f"{value:,.{decimals}f}"


def main():
    print("=" * 65)
    print("TERRATIME4D - MEMBER 3 FINAL REPORT")
    print("=" * 65)

    # Read the latest Earth audit.
    earth_rows = read_csv_rows(EARTH_AUDIT_FILE)
    if not earth_rows:
        raise ValueError("Earth audit CSV contains no records.")

    earth = earth_rows[0]

    summary_count = int(number(earth, "advanced_summary_records"))
    unique_count = int(number(earth, "unique_locations"))
    processing_count = int(number(earth, "processing_log_records"))
    classification_count = int(
        number(earth, "classification_summary_records")
    )
    summary_only_count = int(number(earth, "summary_only_records"))

    earth_elevation = number(earth, "earth_tile_mean_elevation_m")
    earth_slope = number(earth, "earth_tile_mean_slope_degrees")
    earth_roughness_270 = number(
        earth, "earth_tile_mean_roughness_270m_m"
    )
    earth_roughness_630 = number(
        earth, "earth_tile_mean_roughness_630m_m"
    )
    earth_roughness_1350 = number(
        earth, "earth_tile_mean_roughness_1350m_m"
    )

    # Read the actual Moon/Mars summary CSV schema.
    planetary_rows = read_csv_rows(PLANETARY_SUMMARY_FILE)

    planets = {
        row["planet"].strip().lower(): row
        for row in planetary_rows
    }

    if "moon" not in planets or "mars" not in planets:
        raise ValueError(
            "The planetary summary must contain Moon and Mars records."
        )

    moon = planets["moon"]
    mars = planets["mars"]

    def planetary_metrics(row):
        return {
            "elevation": number(
                row, "elevation_area_weighted_mean_km"
            ),
            "slope": number(
                row, "slope_area_weighted_mean_degrees"
            ),
            "roughness": number(
                row, "roughness_area_weighted_mean_km"
            ),
            "roughness_target": number(row, "roughness_target_km"),
            "rows": int(number(row, "rows")),
            "columns": int(number(row, "columns")),
            "valid_slope_cells": int(number(row, "slope_valid_cells")),
            "valid_roughness_cells": int(
                number(row, "roughness_valid_cells")
            ),
        }

    moon_data = planetary_metrics(moon)
    mars_data = planetary_metrics(mars)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report = f"""# TERRATIME4D
# Member 3 - Final Planetary Reference and Comparison Report

## 1. Objective

Member 3 prepared Moon and Mars planetary terrain reference data and
compared their physical terrain measurements with the available Earth
terrain reference data produced by Members 1 and 2.

The work provides planetary reference measurements, comparison outputs,
scientific limitations, and supporting documentation for the next
project stages.

Member 3 focuses on planetary data and analogy assessment. The mission
suitability scoring engine belongs to Member 4, while the final
application and global visualization belong to Member 5.

## 2. Earth Reference Data

Earth reference data was obtained from the Member 2 advanced terrain
summary:

`data/processed/global_terrain/global_advanced_terrain_summary.csv`

The latest audit reports:

- Advanced terrain summary records: {summary_count}
- Unique Earth locations: {unique_count}
- Processing log records: {processing_count}
- Classification summary records: {classification_count}
- Summary records absent from the processing log: {summary_only_count}

The three additional summary-only records are retained because they
contain terrain measurements in the advanced summary. Their presence
does not establish why they are absent from the processing log.

### Earth terrain reference statistics

| Measurement | Mean |
|---|---:|
| Tile mean elevation | {format_number(earth_elevation)} m |
| Tile mean slope | {format_number(earth_slope)} degrees |
| Roughness at 270 m scale | {format_number(earth_roughness_270)} m |
| Roughness at 630 m scale | {format_number(earth_roughness_630)} m |
| Roughness at 1350 m scale | {format_number(earth_roughness_1350)} m |

These Earth values are arithmetic averages of tile-level summary
measurements. They are not a pixel-pooled or area-weighted global
Earth average, and the 648 locations do not represent complete global
Earth coverage.

## 3. Moon Reference Data

The lunar elevation reference is based on the LRO LOLA global elevation
dataset used in the Member 3 analysis.

The processed grid contains {moon_data["rows"]:,} rows and
{moon_data["columns"]:,} columns.

### Area-weighted lunar measurements

| Measurement | Value |
|---|---:|
| Mean elevation | {format_number(moon_data["elevation"])} km |
| Mean slope | {format_number(moon_data["slope"])} degrees |
| Mean roughness | {format_number(moon_data["roughness"])} km |
| Approximate roughness target scale | {format_number(moon_data["roughness_target"], 1)} km |

The lunar elevation raster used in the analysis required aggregation
for practical global processing. Its source raster does not provide
ordinary georeferencing metadata in the form expected by standard
raster workflows, so the analysis uses the documented grid convention.

## 4. Mars Reference Data

The Martian elevation reference is based on the MOLA MEGDR global
elevation dataset.

The processed grid contains {mars_data["rows"]:,} rows and
{mars_data["columns"]:,} columns.

### Area-weighted Martian measurements

| Measurement | Value |
|---|---:|
| Mean elevation | {format_number(mars_data["elevation"])} km |
| Mean slope | {format_number(mars_data["slope"])} degrees |
| Mean roughness | {format_number(mars_data["roughness"])} km |
| Approximate roughness target scale | {format_number(mars_data["roughness_target"], 1)} km |

MOLA MEGDR includes interpolated values in locations where direct
altimeter observations are unavailable. Therefore, the global grid
should not be interpreted as entirely direct measurements.

## 5. Earth, Moon and Mars Comparison

The comparison uses the available Earth tile-level terrain summaries
and the area-weighted Moon and Mars global measurements.

The principal measurements are:

| Measurement | Earth reference | Moon | Mars |
|---|---:|---:|---:|
| Mean elevation | {format_number(earth_elevation / 1000)} km | {format_number(moon_data["elevation"])} km | {format_number(mars_data["elevation"])} km |
| Mean slope | {format_number(earth_slope)} degrees | {format_number(moon_data["slope"])} degrees | {format_number(mars_data["slope"])} degrees |
| Roughness | {format_number(earth_roughness_1350 / 1000)} km at 1350 m scale | {format_number(moon_data["roughness"])} km at approximately 11 km scale | {format_number(mars_data["roughness"])} km at approximately 11 km scale |

The roughness measurements are calculated at different spatial
scales. They must not be treated as directly equivalent measurements.

Earth statistics are unweighted averages of tile-level measurements,
whereas the Moon and Mars values are area-weighted global estimates.
These different sampling and weighting methods must be considered
when interpreting the comparison.

## 6. Scientific Analogy Assessment

Earth locations can provide useful partial analogues for selected
planetary surface conditions and terrain processes.

Examples of useful comparison categories include:

- Impact craters and cratered landscapes.
- Volcanic and basaltic terrain.
- Dry channels, valleys and erosion features.
- Dune fields and dust-related surface processes.
- Polar and cold-region environments.
- Rugged terrain relevant to rover movement and surface operations.

A similar terrain shape does not prove that two locations have the
same geological history or environmental conditions.

Earth cannot fully reproduce lunar vacuum, lunar gravity, the Martian
atmosphere, or planetary radiation conditions. Analogy assessments
must therefore distinguish between physical terrain similarity and
environmental similarity.

The separate analogy assessment is available at:

`results/member3_final_analysis/member3_analogy_assessment.md`

## 7. Generated Outputs

### Global physical analysis

`results/member3_global_analysis_v3/`

- `earth_existing_reference_statistics_v3.csv`
- `earth_reference_audit_v3.csv`
- `earth_reference_tile_records_v3.csv`
- `earth_summary_only_records_v3.csv`
- `moon_mars_physical_summary_v3.csv`
- `moon_mars_latitude_band_analysis_v3.csv`
- `member3_physical_analysis_report_v3.txt`

### Planetary comparison

`results/member3_global_comparison_v3/`

- `planetary_comparison_values_v3.csv`
- `member3_planetary_comparison_report_v3.txt`
- `01_mean_slope_comparison.png`
- `02_earth_roughness_scales.png`
- `03_moon_mars_roughness_comparison.png`
- `04_mean_elevation_comparison.png`
- `05_latitude_slope_comparison.png`
- `06_latitude_roughness_comparison.png`
- `07_planetary_comparison_dashboard.png`

### Elevation maps and analogy assessment

- `results/member3_elevation_maps/`
- `results/member3_final_analysis/member3_analogy_assessment.md`

## 8. Limitations

1. Earth reference coverage is partial and consists of 648 unique
   terrain summary locations.
2. The Earth processing log and classification summary each contain
   645 records, while the advanced summary contains 648 records.
3. Earth averages are tile-level arithmetic averages, not
   area-weighted global statistics.
4. Moon and Mars measurements are area-weighted global estimates.
5. Earth roughness scales differ from the approximately 11 km
   planetary roughness scale used for Moon and Mars.
6. MOLA data includes interpolated values where direct observations
   are unavailable.
7. Similar physical terrain measurements alone cannot establish
   geological or environmental equivalence.
8. The analysis is a reference comparison and does not replace
   mission-specific engineering or environmental validation.

## 9. Handoff to Other Project Members

**Member 4 - Similarity and Mission Scoring Engine**

Use the documented Earth and planetary reference measurements as
inputs for the separate similarity and mission suitability scoring
workflow. Member 4 is responsible for the scoring logic and mission
suitability results.

**Member 5 - 4D Time, Rover Movement and Global Visualization**

Use the documented planetary comparison outputs and generated
figures as supporting inputs for the final application and
visualization workflow.

Member 3 does not claim to have completed Member 4's scoring engine
or Member 5's application.

## 10. Conclusion

Member 3 has prepared global Moon and Mars physical terrain
measurements, updated the Earth reference comparison using the
648-record advanced terrain summary, generated planetary comparison
figures and reports, and documented the scientific limitations of
the analogy assessment.

The results provide a documented reference foundation for the
remaining TERRATIME4D project modules.
"""

    OUTPUT_FILE.write_text(report, encoding="utf-8")

    print("Final report generated successfully.")
    print(f"Earth summary records: {summary_count}")
    print(f"Unique Earth locations: {unique_count}")
    print(f"Processing log records: {processing_count}")
    print(f"Classification records: {classification_count}")
    print(f"Summary-only records: {summary_only_count}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
